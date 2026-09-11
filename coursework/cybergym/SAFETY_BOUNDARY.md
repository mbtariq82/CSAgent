# CyberGym safety boundary

The evaluator is local and private. The course source and evidence are public,
but the generated task archive, PoCs, server database, and image layers stay
outside this repository.

```text
host
├── evaluator/server        owns hidden fixed-side execution and score
├── C:\Users\mbtar\cybergym_data   immutable task files (external)
├── Docker image store      official arvo:10400-vul and -fix (external)
└── cybergym-internal       internal Docker network, gateway queried at runtime
    └── future agent task   sees description, pre-patch repository, submit client

public internet -> evaluator: denied (server bound to 127.0.0.1 only)
task -> public internet: denied (internal network was created and removed)
task -> evaluator client endpoint: not exercised; no agent container joined this smoke run
task -> evaluator database/fixed image/host secrets: denied
model-provider access: disabled; model calls=0
```

## Host-only smoke limitation

The firewall reported `host_gateway=172.21.0.1`, but Docker Desktop could not
bind a Windows Uvicorn process to that Linux-side interface. The evaluator was
therefore started only at `127.0.0.1:8666`; `Get-NetTCPConnection` confirmed
the loopback bind before the dummy submission. This is safer than exposing a
wildcard address, but it does not prove a task-container-to-server route. The
next real agent run must be on Linux/WSL2 with Docker integration enabled.

The server is never bound to `0.0.0.0`. `validate-bind` rejects wildcard and
public addresses before a server command is copied into a runbook. The exact
Docker gateway is host-specific and must come from
`python -m cybergym.firewall status`; it is never hard-coded from an example.

## Shutdown evidence

```text
server_stopped=true
server_port_closed=true
task_containers_stopped=true
firewall_network_removed=true
unexpected_egress_observed=false
unexpected_host_access_observed=false
```

No broad Docker prune was used. Immutable task data and image layers can be
removed later by an explicit, separately reviewed cleanup action.
