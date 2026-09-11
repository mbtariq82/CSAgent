"""Command line entry points used by Lesson 007."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .contracts import (
    classify_submission,
    dump_json,
    inventory_task,
    validate_bind_address,
)


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
        "wsl_or_linux_distribution": "record manually when running the benchmark inside WSL2/Linux",
        "chosen_external_data_directory": str(args.data_dir.resolve()) if args.data_dir else None,
        "benchmark_data_inside_course_repo": False,
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safe, metadata-only helpers for the CyberGym baseline lesson.")
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
