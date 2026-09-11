# CyberGym baseline

This package contains the deterministic, project-owned boundary around the
official CyberGym evaluator:

- `contracts.py` validates the Level 1 file boundary, private evaluator bind,
  and the distinction between transport, execution, and success;
- `cli.py` provides metadata-only preflight, task inventory, and response
  recording commands;
- `CONTRACT.md`, `ENVIRONMENT.md`, `SAFETY_BOUNDARY.md`, and
  `TASK_ARVO_10400.md` record the pinned contract and reproducibility evidence;
- `runs/000_dummy/run.json` is the sanitized result of the first evaluator
  smoke submission.

The helper never runs an uploaded PoC, reads a patched image, starts a server,
or calls a model. CyberGym remains the execution authority.

## Local preflight

Large benchmark data must live outside this repository:

```powershell
python scripts/cybergym_baseline.py preflight `
  --data-dir C:\Users\mbtar\cybergym_data `
  --output C:\Users\mbtar\cybergym_data\preflight.json
```

The preflight is metadata-only. It checks Docker readiness and available
storage without downloading data or starting containers.

## Install the pinned benchmark

Use a dedicated Linux/WSL2 environment rather than the project's Python
environment:

```bash
git clone https://github.com/sunblaze-ucb/cybergym.git
cd cybergym
git checkout c6fe2027d39471375920b92cf1025e23a99ffda5
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev,server]'
python -c "import cybergym; print('cybergym_import=pass')"
```

Download only the selected task into an external data directory:

```bash
hf download sunblaze-ucb/cybergym \
  tasks.json \
  data/arvo/10400/repo-vul.tar.gz \
  data/arvo/10400/description.txt \
  --repo-type dataset \
  --revision bde190ded494e52bc684b66073b436c9d992c7c6 \
  --local-dir /external/path/cybergym_data
```

Use the pinned upstream subset downloader only when expanding beyond the
single-task baseline. Inspect its destination and storage estimate before
starting it.

## Start the isolated evaluator

From the pinned CyberGym checkout:

```bash
python -m cybergym.firewall start
python -m cybergym.firewall status
```

Copy the reported `host_gateway`; never guess or hard-code it. Generate a
fresh `CYBERGYM_API_KEY` and set the same value only in the server and generated
task environments. Start the server on the reported private gateway:

```bash
python -m cybergym.server \
  --host PRIVATE_DOCKER_GATEWAY \
  --port 8666 \
  --mask_map_path mask_map.json \
  --log_dir /external/path/server_poc \
  --db_path /external/path/server_poc/poc.db
```

Before continuing, verify that the server is not listening on `0.0.0.0`, its
storage is not mounted in the agent workspace, and the task network has no
direct public route.

## Generate and validate a Level 1 task

```bash
python -m cybergym.task.gen_task \
  --task-id arvo:10400 \
  --agent-id baseline-smoke-agent \
  --out-dir /external/path/generated/arvo-10400-level1 \
  --data-dir /external/path/cybergym_data/data \
  --server http://PRIVATE_DOCKER_GATEWAY:8666 \
  --mask-map mask_map.json \
  --difficulty level1
```

Then inventory the agent-facing directory from this repository:

```powershell
python scripts/cybergym_baseline.py inspect-task `
  --task-dir C:\external\path\generated\arvo-10400-level1 `
  --task-id arvo:10400 `
  --output C:\external\path\generated\arvo-10400-level1\inventory.json
```

The inventory must contain only `README.md`, `description.txt`,
`repo-vul.tar.gz`, and `submit.sh`. It must not expose the fixed repository or
image, ground-truth patch, reference PoC, evaluator database/logs, revealing Git
history, or Level 2/3-only data.

## Smoke the submission path

Create a harmless four-byte file in the generated task directory and submit it
once with the generated `submit.sh`. A successful HTTP request proves only the
transport and vulnerable-side execution path; it does not imply a crash or a
solved task. Record the sanitized response with:

```powershell
python scripts/cybergym_baseline.py record-submission `
  --response C:\external\path\response.json `
  --transport-exit-code 0 `
  --output C:\external\path\run.json
```

Do not add `--final` for an infrastructure smoke input. The repository stores
only sanitized metadata and hashes, never PoC bytes or raw evaluator logs.

## Shut down

Stop the submission server and remove the benchmark firewall network:

```bash
python -m cybergym.firewall stop-all
```

Verify that the server port and benchmark containers are stopped. Keep pinned
immutable data and image layers unless an explicit cleanup is required; do not
use a broad Docker prune.

## Windows host limitation

The recorded baseline used `127.0.0.1:8666` because Docker Desktop could not
bind the Windows Uvicorn process to the Linux-side gateway. This was a safe
host-only infrastructure smoke, but it did not exercise an agent container.
Run the first real agent evaluation on Linux or WSL2 with Docker integration
enabled and bind to the firewall-reported private gateway.
