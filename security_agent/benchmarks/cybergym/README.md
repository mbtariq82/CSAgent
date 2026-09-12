# CyberGym baseline

This directory contains the production runner for the pinned CyberGym Level 1
task `arvo:10400`. The machine-readable task manifest is
[`config/level1-arvo-10400.json`](config/level1-arvo-10400.json). It contains
only the task identity and the hashes of the four agent-visible files. Runtime
settings come from the generated `submit.sh` and command-line arguments.

## Run

Keep the generated task directory and evaluator storage outside this Git
repository. The task directory must contain exactly `README.md`,
`description.txt`, `repo-vul.tar.gz`, and `submit.sh`.

```powershell
python scripts/cybergym_baseline.py run `
  --task-dir C:\Users\mbtar\cybergym_generated\arvo-10400-level1 `
  --output C:\Users\mbtar\cybergym_runs\arvo-10400.json
```

The runner validates every task-file hash, generates the deterministic
17-byte malformed-MNG candidate, executes the official `submit.sh`, and writes
only redacted fields to the result JSON. It then calls the private
`/verify-agent-pocs` and `/query-poc` endpoints when `CYBERGYM_API_KEY` is set.
The result is `solved` only when the queried record reports a non-timeout
vulnerable crash and a clean patched execution for this one final candidate.

Without a reachable private evaluator, the result is `verification_required`
or `submission_failed`; neither state is a benchmark score. The API key is
read from the environment and never written to the result.

## Boundary

- The agent sees only the vulnerable source archive, description, task README,
  and official submission script.
- The fixed archive/image, reference PoC, patch, evaluator database/logs, and
  host credentials are never copied into the task directory.
- The evaluator must bind to a literal loopback/private address, never a
  wildcard or public address. Public egress is disabled for the agent.
- PoC output and result JSON must be outside the task directory so generated
  files cannot silently expand the agent-visible input set.

The current Windows host has Docker Desktop, but its WSL2 integration cannot
route a task container to a Windows-host evaluator bind. A Linux host or WSL2
distribution with Docker integration enabled is the remaining requirement for
an official final result. The code path and result schema are still exercised
locally with deterministic fixtures and fail closed when the evaluator is
unavailable.

## Development

```powershell
venv\Scripts\python.exe -m pytest -q tests/test_cybergym_contracts.py
python -m ruff check security_agent/benchmarks scripts/cybergym_baseline.py tests/test_cybergym_contracts.py
```

`poc.py` is intentionally deterministic and provider-free. It is a baseline
candidate for this task, not a general-purpose exploit generator.
