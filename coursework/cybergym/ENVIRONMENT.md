# CyberGym environment record

Generated with `python scripts/cybergym_baseline.py preflight`. Values describe
the host used for this lesson; benchmark data is deliberately outside the
course repository.

```text
host_os=Windows 11 with Docker Desktop
wsl_or_linux_distribution=Ubuntu 2 (available, but Docker CLI integration is not enabled in this distro)
architecture=AMD64
python_version=3.12.10
docker_client_version=29.5.3
docker_server_version=29.5.3
available_disk_before=252.50 GB on C:\
chosen_external_data_directory=C:\Users\mbtar\cybergym_data
benchmark_data_inside_course_repo=no
storage_profile=one-task-plus-official-subset
```

The complete CyberGym dataset is approximately 240 GB and the complete
compiled server data is approximately 10 TB. This lesson downloaded only the
selected task's `tasks.json`, `description.txt`, and `repo-vul.tar.gz`, then
pulled the two official `arvo:10400` images needed for the local evaluator.
The official ten-task subset remains the planned next storage expansion; it is
not silently substituted with an unofficial evaluator.

The benchmark process ran with the Windows Python client against Docker
Desktop. WSL2 was checked first, but it cannot reach the Docker daemon on this
host. CyberGym's internal network gateway was `172.21.0.1`; Docker Desktop
would not let Uvicorn bind a Windows process to that Linux-side address. The
smoke run therefore used the stricter host-only fallback
`127.0.0.1:8666`, and no agent container was connected to the evaluator.
This is an infrastructure smoke result, not an agent evaluation. A future
containerized run must use WSL2 with Docker integration enabled (or a Linux
host) and bind to the firewall-reported gateway.

The external upstream checkout needed one platform-only path conversion in its
firewall helper (`\\etc\\squid` to `/etc/squid`) because the Windows Python SDK
otherwise sent a Windows path to Docker. No benchmark logic or course source
was changed; the workaround is intentionally outside this repository.

## Reproduce the preflight

```powershell
python scripts/cybergym_baseline.py preflight `
  --data-dir C:\Users\mbtar\cybergym_data `
  --output C:\Users\mbtar\cybergym_data\preflight.json
```

The preflight does not download files, start containers, or contact a model
provider. It exits non-zero when Docker is not reachable, so a failed check
cannot be mistaken for benchmark evidence.
