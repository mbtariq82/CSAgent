# CyberGym baseline helpers

This directory owns the first benchmark lesson's small, deterministic pieces:

- `contracts.py` validates the Level 1 file boundary, private evaluator bind,
  and the distinction between transport, execution, and success.
- `cli.py` provides metadata-only preflight, task inventory, and response
  recording commands.
- `CONTRACT.md`, `ENVIRONMENT.md`, `SAFETY_BOUNDARY.md`, and
  `TASK_ARVO_10400.md` are the reviewable runbook and evidence.

The helper never runs an uploaded PoC, reads a patched image, starts a server,
or calls a model. CyberGym remains the execution authority. The commands below
are intentionally explicit about where large data lives:

```powershell
# no downloads; capture host readiness
python scripts/cybergym_baseline.py preflight `
  --data-dir C:\Users\mbtar\cybergym_data `
  --output C:\Users\mbtar\cybergym_data\preflight.json

# after the official generator runs outside this repository
python scripts/cybergym_baseline.py inspect-task `
  --task-dir C:\Users\mbtar\cybergym_generated\arvo-10400-level1 `
  --task-id arvo:10400 `
  --output C:\Users\mbtar\cybergym_generated\arvo-10400-level1\inventory.json

# validate a gateway before starting the official server
python scripts/cybergym_baseline.py validate-bind 192.168.48.1
```

For the real run, follow the pinned upstream README command shapes in
`syllabus/LESSON_007.md`. Use WSL2/Linux for the benchmark process, query the
firewall-reported gateway, set a fresh `CYBERGYM_API_KEY` in the server and
generated task environment, and stop the server plus firewall after the smoke
submission. Never commit the generated directory, `poc`, `server_poc`, or raw
logs.
