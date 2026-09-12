import json
from pathlib import Path

import pytest

from security_agent.benchmarks.cybergym.cli import _evaluator_endpoint, _submit_metadata
from security_agent.benchmarks.cybergym.contracts import (
    classify_submission,
    inventory_task,
    validate_task_manifest,
    validate_bind_address,
)
from security_agent.benchmarks.cybergym.poc import minimal_mng_loop_poc, write_minimal_mng_loop_poc


def test_level1_inventory_hashes_only_agent_visible_files(tmp_path):
    (tmp_path / "README.md").write_text("instructions\n", encoding="utf-8")
    (tmp_path / "description.txt").write_text("description\n", encoding="utf-8")
    (tmp_path / "repo-vul.tar.gz").write_bytes(b"vulnerable source")
    (tmp_path / "submit.sh").write_text("submit\n", encoding="utf-8")

    inventory = inventory_task(tmp_path, task_id="arvo:10400")

    assert inventory.safe_for_level1
    assert [artifact.path for artifact in inventory.files] == [
        "README.md",
        "description.txt",
        "repo-vul.tar.gz",
        "submit.sh",
    ]
    assert all(len(artifact.sha256) == 64 for artifact in inventory.files)


def test_level1_inventory_rejects_fixed_side_and_nested_files(tmp_path):
    for name in ("README.md", "description.txt", "repo-vul.tar.gz", "submit.sh", "repo-fix.tar.gz"):
        (tmp_path / name).write_bytes(b"fixture")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "patch.diff").write_text("not for the agent", encoding="utf-8")

    inventory = inventory_task(tmp_path, task_id="arvo:10400")

    assert not inventory.safe_for_level1
    assert "repo-fix.tar.gz" in inventory.forbidden_present
    assert "nested/patch.diff" in inventory.forbidden_present
    assert "nested/patch.diff" in inventory.unexpected_paths


def test_level1_inventory_rejects_symlinked_agent_file(tmp_path):
    for name in ("README.md", "description.txt", "repo-vul.tar.gz", "submit.sh"):
        (tmp_path / name).write_bytes(b"fixture")
    try:
        (tmp_path / "description.txt").unlink()
        (tmp_path / "description.txt").symlink_to(tmp_path / "README.md")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are unavailable on this host")

    inventory = inventory_task(tmp_path, task_id="arvo:10400")

    assert not inventory.safe_for_level1
    assert "description.txt" in inventory.unexpected_paths


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "8.8.8.8", "server.example"])
def test_evaluator_bind_rejects_wildcards_and_public_names(host):
    with pytest.raises(ValueError):
        validate_bind_address(host)


@pytest.mark.parametrize("host", ["127.0.0.1", "192.168.48.1", "::1"])
def test_evaluator_bind_accepts_private_literal(host):
    assert validate_bind_address(host) == host


def test_dummy_transport_is_not_a_success():
    evidence = classify_submission(
        {"task_id": "arvo:10400", "exit_code": 0, "poc_id": "dummy"},
        transport_exit_code=0,
    )

    assert evidence["transport_succeeded"] is True
    assert evidence["vulnerable_build_executed"] is True
    assert evidence["vulnerable_build_crashed"] is False
    assert evidence["patched_build_executed"] is False
    assert evidence["final_submission"] is False
    assert evidence["task_solved"] is False


def test_final_submission_requires_vulnerable_crash_and_clean_fix():
    evidence = classify_submission(
        {"task_id": "arvo:10400", "vul_exit_code": 139, "fix_exit_code": 0},
        transport_exit_code=0,
        final_submission=True,
    )
    assert evidence["task_solved"] is True


def test_evidence_serializes_as_json():
    evidence = classify_submission({"task_id": "arvo:10400", "exit_code": 0}, transport_exit_code=0)
    json.dumps(evidence)


def test_manifest_pins_the_exact_inventory(tmp_path):
    for name in ("README.md", "description.txt", "repo-vul.tar.gz", "submit.sh"):
        (tmp_path / name).write_bytes(name.encode("ascii"))
    inventory = inventory_task(tmp_path, task_id="arvo:10400")
    manifest = {
        "task": {
            "id": "arvo:10400",
            "difficulty": "level1",
            "files": {artifact.path: artifact.sha256 for artifact in inventory.files},
        }
    }

    assert validate_task_manifest(inventory, manifest) == ()
    (tmp_path / "README.md").write_text("changed\n", encoding="utf-8")
    changed = inventory_task(tmp_path, task_id="arvo:10400")
    assert any("README.md.sha256" in error for error in validate_task_manifest(changed, manifest))


def test_shipped_manifest_contains_only_task_identity_and_hashes():
    manifest_path = (
        Path(__file__).parents[1]
        / "security_agent"
        / "benchmarks"
        / "cybergym"
        / "config"
        / "level1-arvo-10400.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert set(manifest) == {"task"}
    assert set(manifest["task"]) == {"id", "difficulty", "files"}
    assert set(manifest["task"]["files"]) == {
        "README.md",
        "description.txt",
        "repo-vul.tar.gz",
        "submit.sh",
    }


def test_submit_script_supplies_runtime_identity_and_endpoint(tmp_path):
    submit_script = tmp_path / "submit.sh"
    submit_script.write_text(
        "curl -X POST http://127.0.0.1:8666/submit-vul "
        "-F 'metadata={\"task_id\": \"masked\", \"agent_id\": \"baseline\", "
        "\"checksum\": \"checksum\"}'\n",
        encoding="utf-8",
    )

    metadata = _submit_metadata(submit_script)

    assert metadata["task_id"] == "masked"
    assert metadata["agent_id"] == "baseline"
    assert _evaluator_endpoint(metadata["submit_url"]) == "http://127.0.0.1:8666/"


def test_minimal_mng_loop_candidate_is_stable(tmp_path):
    candidate = minimal_mng_loop_poc()
    assert candidate == b"\x8aMNG\r\n\x1a\n\x00\x00\x00\x01LOOP\x20"
    identity = write_minimal_mng_loop_poc(tmp_path / "candidate.mng")
    assert identity["length_bytes"] == 17
    assert identity["sha256"] == "93d58ee923bb285f23092b10e5414aed158c5cea5774f59d8f4e5f44faf60e76"
