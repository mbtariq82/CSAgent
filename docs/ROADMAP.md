# Project roadmap

This roadmap organizes development around benchmark evidence. Each milestone
must leave behind reproducible tests, pinned inputs, and an explicit record of
what the result proves. A capability is retained only when it improves a
measured outcome or closes a demonstrated safety gap.

## M0 — CyberGym evaluation boundary

- [x] Pin the CyberGym source and dataset revisions used by the baseline.
- [x] Validate the Level 1 agent-visible file contract.
- [x] Separate transport, vulnerable execution, patched execution, final
  submission, and task success in machine-readable results.
- [x] Generate one deterministic final candidate and execute the official
  submission client.
- [x] Validate task hashes, bind addresses, and non-leakage controls before a
  candidate can be submitted.
- [ ] Run the candidate through the private evaluator from a containerized
  agent environment on Linux or WSL2 with Docker integration enabled.

## M1 — Minimal agent core (B0)

- [ ] Define provider-neutral task, tool request/result, run budget, agent
  result, and run-metrics contracts.
- [ ] Add a deterministic scripted model for end-to-end tests.
- [ ] Implement one bounded action/observation loop with an isolated shell
  tool, explicit termination, and an append-only trace.
- [x] Implement a CyberGym adapter that exposes only permitted Level 1 inputs
  and requires one explicit final PoC path.
- [ ] Freeze the first scored configuration after the private evaluator run.

## M2 — Reproducible evaluation

- [ ] Add immutable experiment manifests containing code, benchmark, model,
  image, task, budget, and prompt revisions.
- [ ] Store replayable, redacted traces and artifact hashes.
- [ ] Add resumable batch execution with bounded concurrency and clear
  infrastructure-failure classification.
- [ ] Establish smoke, development, and locked manifests.
- [ ] Publish the official ten-task CyberGym subset baseline with per-task
  outcomes, cost, latency, and a failure taxonomy.

## M3 — Evidence-driven capability growth

- [ ] Measure repository-navigation waste, then evaluate bounded file and
  symbol tools against the frozen baseline.
- [ ] Add controlled build/execution and sanitizer evidence handling.
- [ ] Treat PoCs as binary-safe artifacts with hashes, size limits, and one
  explicit final candidate.
- [ ] Evaluate deterministic mutation, execution-guided iteration, candidate
  minimization, and skeptical final selection as separate ablations.
- [ ] Add explicit hypothesis state or branching only if equal-budget results
  justify the added complexity.

## M4 — Harness hardening and CyberGym v1

- [ ] Threat-model the agent, benchmark adapter, evaluator, secrets, traces,
  and reward-hacking paths.
- [ ] Test repository prompt injection, traversal, symlink escape, archive
  abuse, process limits, output limits, secret access, and network isolation.
- [ ] Prove the agent cannot access fixed-side artifacts, evaluator state,
  previous answers, or public egress during locked runs.
- [ ] Freeze CyberGym Agent v1 with score, cost, safety results, limitations,
  and representative sanitized traces.

## M5 — Cross-benchmark adapters

- [ ] Add a Cybench adapter and measure transfer across CTF task families.
- [ ] Add a controlled CVE-Bench adapter with bounded HTTP/browser state and
  goal-specific verifier evidence.
- [ ] Add transactional patch workflows for BountyBench and CRSBench.
- [ ] Add the staged CyberGym-E2E output contract for discovery, PoC,
  repair, regression safety, and root-cause validation.

The agent core must remain benchmark-neutral. Benchmark-specific packaging,
credentials, services, and scoring belong behind adapters; official evaluators
remain the authority for pass/fail results.

## M6 — Comparative evaluation and release

- [ ] Reproduce at least one open reference agent under normalized budgets.
- [ ] Compare static analysis, fuzzing, retrieval, memory, branching, critics,
  and specialist roles through controlled ablations.
- [ ] Run a locked cross-benchmark matrix from a clean environment.
- [ ] Publish architecture, threat model, methodology, negative results,
  contamination risks, cost curves, and sanitized traces.
- [ ] Package a one-command smoke path and freeze a versioned release.

See [BENCHMARKS_AND_AGENTS.md](BENCHMARKS_AND_AGENTS.md) for benchmark and
reference-implementation links.
