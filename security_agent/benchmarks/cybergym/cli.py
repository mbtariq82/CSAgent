"""Command-line entry points for the CyberGym baseline boundary."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .contracts import (
    classify_submission,
    dump_json,
    inventory_task,
    validate_task_manifest,
    validate_bind_address,
)
from .poc import write_minimal_mng_loop_poc

DEFAULT_CONFIG = Path(__file__).with_name("config") / "level1-arvo-10400.json"
MAX_POC_BYTES = 10 * 1024 * 1024
VERIFY_PATH = "/verify-agent-pocs"
QUERY_PATH = "/query-poc"


def _command(*args: str) -> dict[str, Any]:
    executable = shutil.which(args[0])
    if executable is None:
        return {"command": list(args), "available": False, "returncode": None, "stdout": "", "stderr": "not found"}
    process = subprocess.run(args, capture_output=True, text=True, check=False, timeout=30)
    return {
        "command": list(args),
        "available": True,
        "returncode": process.returncode,
        "stdout": process.stdout.strip(),
        "stderr": process.stderr.strip(),
    }


def _preflight(args: argparse.Namespace) -> int:
    docker_info = _command("docker", "info", "--format", "{{json .}}")
    docker_version = _command("docker", "version", "--format", "{{json .Server}}")
    result = {
        "host_os": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "docker_client": _command("docker", "--version"),
        "docker_info": docker_info,
        "docker_server": docker_version,
        "wsl_distribution": _command("wsl.exe", "-l", "-q"),
        "chosen_external_data_directory": str(args.data_dir.resolve()) if args.data_dir else None,
        "benchmark_data_inside_project_repo": False,
        "storage_profile": "one-task-plus-official-subset",
    }
    if args.data_dir:
        args.data_dir.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(args.data_dir)
        result["available_disk_before_bytes"] = usage.free
    dump_json(result, args.output)
    return 0 if docker_info.get("returncode") == 0 else 2


def _inspect_task(args: argparse.Namespace) -> int:
    inventory = inventory_task(args.task_dir, task_id=args.task_id, difficulty=args.difficulty)
    dump_json(inventory.to_dict(), args.output)
    return 0 if inventory.safe_for_level1 else 2


def _record_submission(args: argparse.Namespace) -> int:
    response = json.loads(args.response.read_text(encoding="utf-8"))
    evidence = classify_submission(response, transport_exit_code=args.transport_exit_code, final_submission=args.final)
    evidence["raw_response_fields"] = sorted(response)
    dump_json(evidence, args.output)
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _submit_metadata(submit_path: Path) -> dict[str, str]:
    """Read only the public task metadata embedded in the official script."""

    text = submit_path.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for field in ("task_id", "agent_id", "checksum"):
        match = re.search(rf'"{field}"\s*:\s*"([^"]+)"', text)
        if match is None:
            raise ValueError(f"submit.sh is missing metadata field: {field}")
        values[field] = match.group(1)
    submit_url = re.search(r"https?://[^\s\\]+/submit-vul", text)
    if submit_url is None:
        raise ValueError("submit.sh is missing the CyberGym submission URL")
    values["submit_url"] = submit_url.group(0)
    return values


def _submission_response(stdout: str) -> dict[str, Any]:
    """Extract the JSON object printed by submit.sh without retaining logs."""

    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def _post_json(url: str, payload: dict[str, Any], *, api_key: str, timeout: int) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-API-Key": api_key},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - endpoint is validated before use
            body = response.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return {"http_status": response.status, "response": parsed}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"http_status": exc.code, "error": body[:500]}
    except URLError as exc:
        return {"http_status": None, "error": str(exc.reason)}
    except TimeoutError as exc:
        return {"http_status": None, "error": str(exc)}


def _evaluator_endpoint(submit_url: str) -> str:
    """Derive the private evaluator endpoint from CyberGym's submit.sh."""

    parsed = urlparse(submit_url)
    if parsed.scheme != "http" or not parsed.hostname:
        raise ValueError("CyberGym submission URL must use HTTP with a literal host")
    validate_bind_address(parsed.hostname)
    if parsed.path != "/submit-vul" or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("CyberGym submission URL must end with /submit-vul")
    if parsed.username or parsed.password:
        raise ValueError("CyberGym submission URL must not contain credentials")
    return f"{parsed.scheme}://{parsed.netloc}/"


def _run_baseline(args: argparse.Namespace) -> int:
    manifest = _load_json(args.config)
    task = manifest.get("task")
    if not isinstance(task, dict):
        raise ValueError("manifest.task must be an object")
    task_dir = args.task_dir.resolve()
    submit_path = task_dir / "submit.sh"
    if not submit_path.is_file():
        raise ValueError(f"task directory has no submit.sh: {task_dir}")
    inventory = inventory_task(task_dir, task_id=str(task["id"]), difficulty=str(task["difficulty"]))
    manifest_errors = validate_task_manifest(inventory, manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if manifest_errors:
        dump_json(
            {
                "schema_version": 1,
                "run_kind": "cybergym_final_evaluation",
                "status": "invalid_task",
                "created_at": _utc_now(),
                "manifest": str(args.config.resolve()),
                "task_inventory": inventory.to_dict(),
                "errors": list(manifest_errors),
            },
            args.output,
        )
        return 2

    metadata = _submit_metadata(submit_path)
    endpoint = _evaluator_endpoint(metadata["submit_url"])

    poc_path = (args.poc_path or args.output.with_suffix(".poc")).resolve()
    if task_dir in poc_path.parents:
        raise ValueError("PoC output must be outside the agent-visible task directory")
    poc_identity = write_minimal_mng_loop_poc(poc_path)
    if int(poc_identity["length_bytes"]) > MAX_POC_BYTES:
        raise ValueError("generated PoC exceeds the size limit")
    bash = shutil.which("bash")
    if bash is None:
        raise ValueError("bash is required to execute the official submit.sh")
    started_at = _utc_now()
    try:
        process = subprocess.run(
            [bash, str(submit_path), str(poc_path)],
            capture_output=True,
            text=True,
            check=False,
            cwd=task_dir,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        process = None
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        response = {}
        transport_exit_code = 124
    else:
        stdout = process.stdout
        stderr = process.stderr
        response = _submission_response(stdout)
        transport_exit_code = process.returncode

    evidence = classify_submission(response, transport_exit_code=transport_exit_code, final_submission=False)
    result: dict[str, Any] = {
        "schema_version": 1,
        "run_kind": "cybergym_final_evaluation",
        "status": "submission_failed" if not evidence["transport_succeeded"] else "awaiting_verification",
        "started_at": started_at,
        "finished_at": _utc_now(),
        "manifest": str(args.config.resolve()),
        "benchmark": "CyberGym",
        "task": {"id": task.get("id"), "difficulty": task.get("difficulty")},
        "environment": {
            "host_os": platform.platform(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "evaluator_endpoint": endpoint,
            "public_egress": False,
        },
        "task_inventory": inventory.to_dict(),
        "poc": poc_identity,
        "submission": {
            "agent_task_id": metadata["task_id"],
            "agent_id": metadata["agent_id"],
            "transport_exit_code": transport_exit_code,
            "response_fields": sorted(response),
            "stderr_present": bool(stderr.strip()),
            "stdout_non_json_present": any(line.strip() and not line.strip().startswith("{") for line in stdout.splitlines()),
        },
        "verification": {"status": "not_run", "reason": "CYBERGYM_API_KEY is not set"},
        "evidence": evidence,
        "model_calls": 0,
    }
    if not response and (stderr.strip() or stdout.strip()):
        result["submission"]["failure_reason"] = (stderr.strip() or stdout.strip())[:500]

    api_key = os.getenv("CYBERGYM_API_KEY")
    if response and response.get("poc_id") and api_key:
        verify_result = _post_json(
            urljoin(endpoint, VERIFY_PATH.lstrip("/")),
            {"agent_id": metadata["agent_id"]},
            api_key=api_key,
            timeout=args.timeout,
        )
        query_result = _post_json(
            urljoin(endpoint, QUERY_PATH.lstrip("/")),
            {"agent_id": metadata["agent_id"], "task_id": metadata["task_id"]},
            api_key=api_key,
            timeout=args.timeout,
        )
        records = query_result.get("response")
        matching = next(
            (record for record in records if isinstance(record, dict) and record.get("poc_id") == response.get("poc_id")),
            None,
        ) if isinstance(records, list) else None
        verified = (
            matching is not None
            and verify_result.get("http_status") == 200
            and query_result.get("http_status") == 200
        )
        result["verification"] = {
            "status": "completed" if verified else "failed",
            "verify": {"http_status": verify_result.get("http_status")},
            "query": {"http_status": query_result.get("http_status")},
        }
        if verified:
            result["evidence"] = classify_submission(matching, transport_exit_code=0, final_submission=True)
            result["status"] = "solved" if result["evidence"]["task_solved"] else "unsolved"
        else:
            result["verification"]["error"] = {
                "verify": verify_result.get("error"),
                "query": query_result.get("error", "matching PoC record not returned"),
            }
            result["status"] = "verification_failed"
    elif response and response.get("poc_id"):
        result["status"] = "verification_required"

    dump_json(result, args.output)
    return 0 if result["status"] in {"solved", "unsolved", "verification_required"} else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproducible CyberGym baseline runner and safety checks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Capture host and Docker readiness without downloading data.")
    preflight.add_argument("--data-dir", type=Path, required=True)
    preflight.add_argument("--output", type=Path)
    preflight.set_defaults(func=_preflight)

    inspect = subparsers.add_parser("inspect-task", help="Hash and validate an agent-facing Level 1 task directory.")
    inspect.add_argument("--task-dir", type=Path, required=True)
    inspect.add_argument("--task-id", required=True)
    inspect.add_argument("--difficulty", default="level1")
    inspect.add_argument("--output", type=Path)
    inspect.set_defaults(func=_inspect_task)

    record = subparsers.add_parser("record-submission", help="Classify a sanitized submit-vul JSON response.")
    record.add_argument("--response", type=Path, required=True)
    record.add_argument("--transport-exit-code", type=int, required=True)
    record.add_argument("--final", action="store_true")
    record.add_argument("--output", type=Path, required=True)
    record.set_defaults(func=_record_submission)

    run = subparsers.add_parser("run", help="Generate and submit the deterministic Level 1 candidate.")
    run.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    run.add_argument("--task-dir", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True, help="Machine-readable result path outside the task directory.")
    run.add_argument("--poc-path", type=Path, help="Optional PoC path; defaults beside --output.")
    run.add_argument("--timeout", type=int, default=1200)
    run.set_defaults(func=_run_baseline)

    bind = subparsers.add_parser("validate-bind", help="Reject wildcard/public evaluator binds.")
    bind.add_argument("host")
    bind.set_defaults(func=lambda args: (print(validate_bind_address(args.host)) or 0))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
