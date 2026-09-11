# Benchmark-Driven Cybersecurity Agent Engineering

## Course goal

Build one portfolio-grade cybersecurity agent by measuring it from the beginning. The first security milestone is a **minimal CyberGym Level 1 agent**, not a speculative repository scanner. Every later capability must earn its place by improving a frozen benchmark slice, reducing cost, improving reliability, or closing a demonstrated safety gap.

The finished system will accept several benchmark task formats through adapters while keeping one small agent core. It will reproduce known vulnerabilities in CyberGym, solve a controlled sample of CTF and web-CVE tasks, produce and verify defensive patches, and complete a discover–prove–fix workflow in CyberGym-E2E.

This is an engineering course, not a leaderboard-chasing recipe. The durable skills are experiment design, agent/tool interfaces, code navigation, dynamic analysis, PoC generation, patch validation, isolation, observability, and honest evaluation.

## What changes from the previous course

- Weeks 1 and Lessons 001–006 remain the completed software/ML foundation.
- Lesson 007 now begins with CyberGym's real task and evaluator contract.
- Every unfinished lesson is implemented by the assistant as one focused pull request and learned through review; the learner is not expected to write the implementation by hand.
- The first agent is deliberately small: one model, one shell tool, one loop, one final artifact, and a trace.
- Domain models, retrieval, planners, memory, multiple agents, and orchestration frameworks are added only after a baseline failure justifies them.
- Benchmark adapters replace a product-specific scan pipeline as the main architecture.
- LangChain, LangGraph, FastAPI, Temporal, and a graphical interface are optional extensions, not calendar-driven requirements.
- The core course finishes with cross-benchmark evidence rather than a feature checklist.

The incomplete pre-redesign `security_agent/domain.py` and provider experiments are scratch work. Preserve them until the new contracts make clear what should be reused, rewritten, or removed.

## The system we are building

```text
official benchmark task
        |
        v
benchmark adapter -----> normalized task + evaluator contract
        |                              |
        v                              v
minimal agent core <---- budgets, policy, and run configuration
        |
        +---- model
        +---- isolated shell / file / analysis tools
        +---- run-local working memory
        |
        v
PoC, flag, finding, or patch
        |
        v
official evaluator -----> trace + score + cost + failure class
```

The benchmark owns truth. The agent never decides whether it succeeded.

## Baseline B0: the minimal harness

Freeze this baseline before adding features:

- one provider-neutral chat-model interface;
- one `shell` tool executed only inside the task workspace/container;
- a simple action/observation loop with an explicit step, token, time, and output budget;
- no framework, sub-agents, vector database, long-term memory, static-analysis ensemble, or autonomous web browsing;
- a final-answer protocol that names exactly one artifact;
- append-only JSONL events plus a compact run summary;
- deterministic fake-model tests for the loop and one real-model run on the official CyberGym development subset.

The baseline may be weak. Its purpose is to make every later improvement measurable and attributable.

## Benchmark ladder

| Order | Benchmark | Capability under test | Course role |
| --- | --- | --- | --- |
| 1 | [CyberGym Level 1](https://www.cybergym.io/cybergym/) | Given a vulnerability description and pre-patch repository, create a PoC that fails on the vulnerable build but not the patched build | Primary benchmark and continuous regression suite |
| 2 | [Cybench](https://cybench.github.io/) | Interactive professional CTF tasks across web, crypto, reverse engineering, forensics, pwn, and misc | Tests whether the harness transfers beyond source-code PoCs |
| 3 | [CVE-Bench](https://github.com/uiuc-kang-lab/cve-bench) | Reproduce critical web CVEs against isolated applications | Adds HTTP, sessions, services, and black-box evidence |
| 4 | [BountyBench](https://github.com/bountybench/bountybench) and [CRSBench in ACESEvals](https://github.com/microsoft/ACESEvals) | Detect/exploit/patch workflows and PoV-grounded vulnerability patching | Makes defensive patching and invariant preservation first-class |
| 5 | [CyberGym-E2E](https://www.cybergym.io/cybergym-e2e/) | Discover a vulnerability, generate a PoC, patch it, and preserve functionality | Required end-to-end capstone benchmark |

Optional advanced tracks are [ExploitGym](https://www.cybergym.io/exploitgym/) for exploit generation, [CTI-REALM in ACESEvals](https://github.com/microsoft/ACESEvals) for threat-intelligence/detection work, and the [AIxCC competition archive](https://archive.aicyberchallenge.com/) for production-scale cyber reasoning systems. They are not required for the core course because their risk, infrastructure, or specialization would distort the main learning path.

See [BENCHMARKS_AND_AGENTS.md](BENCHMARKS_AND_AGENTS.md) for exact repositories, successful systems, papers, and what to study from each.

## Pull-request learning contract

Beginning with W02D01, every unchecked lesson maps to exactly one PR:

```text
assistant implements and tests the lesson
        |
        v
assistant opens a focused PR with a guided review route
        |
        v
learner reviews decisions, tests, evidence, and security boundaries
        |
        +---- requests changes --> assistant updates the same PR
        |
        v
learner approves and merges
        |
        v
next lesson branches from the merged result
```

The PR is the lesson artifact. It must contain a concise outcome, motivation, review order, important decisions and alternatives, exact test/benchmark evidence, security and benchmark-integrity notes, reviewer questions, explicit non-goals, and the lesson definition of done.

The assistant owns implementation. The learner's work is to understand and challenge the diff, inspect or run the evidence, discuss trade-offs, request revisions, and decide whether it is ready to merge. The assistant never merges a lesson PR without explicit instruction.

Fast deterministic tests run in CI. Paid model calls, large downloads, secret-bearing provider access, and heavy Docker benchmark runs execute only in an authorized environment; their pinned, sanitized results are attached to the PR. Mock results must never be presented as official benchmark results.

Benchmark archives, Docker layers, PoCs, evaluator databases, hidden/fixed-side data, credentials, and sensitive raw traces stay out of Git. A PR is an external disclosure boundary even when its repository is private.

See [PR_LEARNING_WORKFLOW.md](PR_LEARNING_WORKFLOW.md) for branch naming, the required PR template, reviewer responsibilities, evidence rules, and lesson completion states.

## Evaluation contract

### Never develop on the headline number

For each benchmark, create three manifests:

- `smoke`: one or two cheap tasks used to prove wiring;
- `dev`: a representative slice used for prompt and harness changes;
- `locked_eval`: untouched while developing and opened only at planned checkpoints.

CyberGym's official ten-task subset is infrastructure-friendly relative to the full suite, but it was intentionally selected to contain five easier and five difficult tasks. Treat it as a development set, not an unbiased estimate of full-benchmark performance.

### Record every run

Every result must include:

- benchmark name, version/commit, task ID, difficulty, and manifest hash;
- agent and prompt version, model identifier, provider settings, and container image digests;
- final-submission success, not merely whether any intermediate candidate happened to work;
- attempts, steps, tool calls, input/output/cache tokens, estimated cost, and wall time;
- termination reason and a failure class;
- final artifact hash and evaluator output;
- whether dynamic execution, network access, memory, scanners, or multiple models were enabled.

Do not average unlike benchmark metrics into a single vanity score. Report each benchmark separately and show cost–success trade-offs.

### Change one meaningful variable at a time

Each weekly experiment has a hypothesis, frozen task manifest, baseline, treatment, budget, and decision. Keep a feature only when it improves effectiveness, efficiency, reliability, or safety. Re-run the current baseline when the model, provider, benchmark version, or infrastructure changes.

## Safety and benchmark integrity

- Work only inside course fixtures, official benchmark containers, or systems you own and explicitly authorize.
- Deploy CyberGym and every evaluator locally on a host-controlled private interface. Never bind its submission endpoint to `0.0.0.0` or expose it to the public internet.
- Deny direct agent egress by default. If a provider endpoint is required, route only that endpoint through the benchmark's allowlist proxy and log the exception.
- Do not let the agent access a patched image, hidden tests, reference PoCs, solution files, repository history, issue trackers, release notes, or benchmark answer stores.
- Remove `.git` and known reference-artifact paths from dynamic task images as required by the benchmark.
- Treat repositories, task descriptions, build output, tool output, and retrieved text as untrusted data that can contain prompt injection.
- Separate the agent container, evaluator, credentials, and host. The agent must not control its scorer or inspect evaluator state.
- Require bounded commands, processes, disk, memory, time, output, and artifact size. Preserve task containers for forensic review when a policy violation occurs.
- A crash on both pre- and post-patch builds is not a CyberGym success. Keep exactly one final submission for the headline metric.
- Do not publish newly discovered vulnerabilities before coordinated disclosure. Convert only already-public or synthetic cases into course material.
- Optional exploit-generation work requires the same isolation and is never run against public targets.

## Practical environment strategy

CyberGym is not a small Python package. The official repository reports roughly 240 GB for the complete benchmark dataset, about 130 GB for binary-only server data, and roughly 10 TB for the full compiled server data. The course therefore starts with one official task and the official ten-task subset, records storage estimates before downloading, and postpones large batch runs until the infrastructure week.

Use Linux or WSL2 with Docker for benchmark execution. Keep the current Windows workspace for course code if desired, but run Linux benchmark containers through a documented boundary. Pin benchmark commits and container digests; never silently track `main` during an experiment.

## Working rhythm

There are 16 weeks with six PR-based lessons per week: 96 lessons total. Lessons 001–006 remain completed historical work; the remaining 90 lessons use the new review workflow unless the learner asks to recreate the earlier work as PRs.

One lesson PR is active at a time by default. It begins from the merged previous lesson, stays focused on that lesson's primary idea, and ends with executable evidence: a passing contract test, saved trace, official evaluator result, comparison table, or documented keep/reject decision. A new capability is not complete merely because its code runs or because a PR exists.

Review and revision are part of the lesson rather than overhead. The assistant may open a draft while an expensive evaluation is still running, but marks it ready only when the definition of done is satisfied. The learner approves and merges before the next lesson starts. The seventh day remains available for deeper review, catch-up, or rest.

---

## Phase 1 — Completed foundation

### Week 1 — Reliable Python and ML program boundaries

- [x] **W01D01 — Establish a trustworthy baseline.** Inspect the FashionMNIST program, record behavior, understand tensor and batch contracts, and protect the checkpoint.
- [x] **W01D02 — Make the experiment configurable.** Centralize stable settings and construct the loss and optimizer through explicit configuration boundaries.
- [x] **W01D03 — Build a reusable data pipeline.** Separate datasets from dataloaders, make shuffle and worker behavior explicit, and inspect real batches.
- [x] **W01D04 — Make training safe to import and test.** Implement a correct one-epoch boundary, sample-weighted metrics, and a smoke test.
- [x] **W01D05 — Make evaluation trustworthy.** Test uneven batches, empty input, non-finite loss, evaluation mode, and inference without gradients.
- [x] **W01D06 — Make program boundaries import-safe.** Add explicit entry points and paired smoke tests, protect the checkpoint, and create the `security_agent` package.

**Milestone:** a small Python/ML program with explicit dependencies, trustworthy metrics, fast tests, and no import-time side effects.

---

## Phase 2 — CyberGym first: baseline, measurement, and core capability

### Week 2 — Touch the benchmark before designing the agent

- [ ] **W02D01 — Learn CyberGym by running its contract.** Pin the official repository, select one official subset task, generate its Level 1 workspace, submit a harmless dummy artifact, inspect the evaluator response, and document the isolation boundary.
- [ ] **W02D02 — Define only the cross-benchmark contracts B0 needs.** Add typed `Task`, `AgentResult`, `ToolRequest`, `ToolResult`, `RunBudget`, and `RunMetrics` values plus a fake task adapter; defer vulnerability-domain models.
- [ ] **W02D03 — Add one model boundary.** Implement a provider-neutral chat interface and deterministic scripted fake, then make one real call with explicit settings and usage capture.
- [ ] **W02D04 — Build the minimal action/observation loop.** Support one isolated shell tool, bounded output, explicit termination, and an append-only trace without LangChain or LangGraph.
- [ ] **W02D05 — Adapt B0 to CyberGym.** Load the generated task, provide only permitted files and description, require one final PoC path, invoke the official submission path, and store the scorer output without interpreting it as model text.
- [ ] **W02D06 — Freeze and run B0.** Pass fake-model end-to-end tests, run one real official task, publish the B0 configuration card, and record success or failure honestly.

**Milestone:** the smallest useful agent has produced a fully reproducible CyberGym run through the official evaluator.

### Week 3 — Turn runs into experiments

- [ ] **W03D01 — Design the experiment manifest.** Pin task IDs, benchmark commit, prompt, model, image digests, budgets, seeds, and expected artifact type in one immutable run specification.
- [ ] **W03D02 — Make traces replayable.** Record model messages, tool inputs/outputs, truncation, timestamps, usage, artifact hashes, and evaluator results with secret redaction.
- [ ] **W03D03 — Build a batch runner.** Add bounded concurrency, per-task isolation, idempotent run IDs, retries only for infrastructure failures, and cooperative cancellation.
- [ ] **W03D04 — Resume without corrupting evidence.** Checkpoint completed steps, distinguish agent failure from evaluator/infrastructure failure, and prove interrupted batches can resume.
- [ ] **W03D05 — Create smoke, dev, and locked manifests.** Stratify by project, language, vulnerability description, and expected PoC length without reading solutions.
- [ ] **W03D06 — Establish the ten-task development baseline.** Run B0 on the official subset, report final-submission success, cost, latency, variance, and a manual taxonomy of failures.

**Milestone:** agent changes can be compared on identical tasks with complete provenance and no hand-scored outcomes.

### Week 4 — Repository navigation and vulnerability localization

- [ ] **W04D01 — Measure navigation waste.** Use B0 traces to quantify repeated reads, oversized output, irrelevant files, and time spent before the first useful hypothesis.
- [ ] **W04D02 — Add bounded file tools.** Introduce list, search, and line-range read tools with root confinement and compact, line-numbered output; retain shell for builds.
- [ ] **W04D03 — Extract clues from the task description.** Identify likely weakness class, parser/input format, entry point, named symbols, and uncertainty without inventing facts.
- [ ] **W04D04 — Build a lightweight repository map.** Index filenames, symbols, manifests, build targets, harnesses, and call-site references with deterministic tools.
- [ ] **W04D05 — Add source-to-entry-point investigation.** Make the agent trace a candidate defect back to an input path and record evidence for and against the hypothesis.
- [ ] **W04D06 — Run the navigation ablation.** Compare B0 with bounded navigation on the same dev manifest; keep only changes that improve score, cost, or useful-work ratio.

### Week 5 — Dynamic analysis and crash understanding

- [ ] **W05D01 — Reproduce builds reliably.** Discover build instructions, cache only safe dependencies, classify build failures, and capture compiler/sanitizer versions.
- [ ] **W05D02 — Read sanitizer evidence.** Parse ASan, UBSan, MSan, and timeout signals into frames and fault classes while preserving raw output.
- [ ] **W05D03 — Add a controlled execution tool.** Enforce cwd, command allowlists/policy, process and time limits, output caps, and no network inside the task container.
- [ ] **W05D04 — Separate target crashes from noise.** Detect harness failures, startup crashes, flaky behavior, and candidates that crash both vulnerable and patched builds.
- [ ] **W05D05 — Feed concise execution feedback back to the model.** Summarize only observable facts, retain raw provenance, and prevent tool output from issuing instructions.
- [ ] **W05D06 — Evaluate dynamic access.** Compare static-only and dynamic variants under equal budgets and publish which task classes benefit.

### Week 6 — PoC synthesis, mutation, and minimization

- [ ] **W06D01 — Model PoCs as artifacts, not chat text.** Support binary-safe writes, size limits, MIME/format hints, hashes, and one explicit final candidate.
- [ ] **W06D02 — Generate seeds from input grammar clues.** Use examples, parsers, fuzz harnesses, and file signatures without consulting hidden/reference PoCs.
- [ ] **W06D03 — Add deterministic mutators.** Implement bounded byte, token, length, structure, and dictionary mutations with recorded seeds.
- [ ] **W06D04 — Use execution-guided iteration.** Classify observations, retain promising candidates, avoid resubmitting duplicates, and stop unproductive loops.
- [ ] **W06D05 — Minimize and validate candidates.** Reduce a triggering input while preserving the crash signature and protect against accidental evaluator overfitting.
- [ ] **W06D06 — Measure the PoC pipeline.** Report success by input length, project, weakness, attempts, and mutation strategy on the frozen dev set.

**Milestone:** the agent can navigate a real codebase, form a vulnerability hypothesis, generate binary-safe candidates, and use controlled runtime evidence to improve them.

### Week 7 — Reasoning control without framework lock-in

- [ ] **W07D01 — Diagnose failed trajectories.** Label premature commitment, shallow localization, build thrashing, repeated commands, context loss, and budget exhaustion.
- [ ] **W07D02 — Add explicit run state.** Track hypotheses, supporting/contradicting evidence, candidate artifacts, crash signatures, remaining budget, and termination reason.
- [ ] **W07D03 — Separate plan, act, and review.** Use small typed phases inside the direct loop and test invalid transitions and recovery.
- [ ] **W07D04 — Explore multiple hypotheses within one agent.** Allocate bounded branches, share only verified evidence, and choose a final candidate using observable results.
- [ ] **W07D05 — Add a candidate critic.** Challenge whether a PoC matches the described vulnerability and penalize crashes that appear unrelated or non-specific.
- [ ] **W07D06 — Ablate the controller.** Compare direct loop, explicit state, branching, and critic variants at the same model and budget.

### Week 8 — Memory, retrieval, and contamination control

- [ ] **W08D01 — Separate three kinds of memory.** Distinguish context within a run, resumable run state, and cross-task knowledge; keep evaluation outcomes out of reusable memory.
- [ ] **W08D02 — Build retrieval only for large repositories.** Compare lexical, symbol, call-graph, and embedding retrieval against exact relevant-file recall and cost.
- [ ] **W08D03 — Create abstract strategy notes.** Store general debugging and input-format lessons without task IDs, patches, PoC bytes, issue text, or solution-bearing snippets.
- [ ] **W08D04 — Audit for leakage.** Scan prompts, caches, traces, images, `.git`, temporary paths, web tools, and model-accessible metadata for answer channels.
- [ ] **W08D05 — Test memory on held-out projects.** Measure transfer across project families and reject gains that disappear when identifiers and near-duplicates are removed.
- [ ] **W08D06 — Choose the smallest retained memory design.** Publish the ablation and update the agent card with its contamination assumptions.

### Week 9 — Secure the harness and freeze CyberGym v1

- [ ] **W09D01 — Threat-model the agent/evaluator system.** Identify assets, trust boundaries, credentials, scorer authority, untrusted inputs, and reward-hacking routes.
- [ ] **W09D02 — Defend against repository prompt injection.** Seed malicious comments, docs, filenames, and tool output and enforce the separation between data and control.
- [ ] **W09D03 — Test filesystem and process isolation.** Cover traversal, symlink escape, archive abuse, oversized files, fork/process bombs, and secret access.
- [ ] **W09D04 — Test network isolation.** Prove direct egress is denied, provider traffic follows the allowlist, the evaluator is private, and web-mediated leakage is unavailable.
- [ ] **W09D05 — Audit scorer integrity.** Verify the agent cannot read post-patch artifacts, hidden state, reference inputs, previous final answers, or evaluator credentials.
- [ ] **W09D06 — Run the first locked CyberGym checkpoint.** Freeze CyberGym Agent v1 and publish score, cost, safety results, limitations, and representative sanitized trajectories.

**Milestone:** a measured and isolated CyberGym agent whose design is supported by ablations rather than feature accumulation.

---

## Phase 3 — Transfer the same agent across cybersecurity benchmarks

### Week 10 — Cybench and broad CTF transfer

- [ ] **W10D01 — Map the Cybench contract.** Inspect task, Kali environment, action/observation loop, flag evaluator, subtasks, and official scoring.
- [ ] **W10D02 — Implement a Cybench adapter.** Translate its task and submission protocol without adding benchmark-specific logic to the agent core.
- [ ] **W10D03 — Add task-profile routing.** Recognize web, crypto, reverse, forensics, pwn, and misc capabilities and select only installed tools.
- [ ] **W10D04 — Add interactive service handling.** Support local task servers, sessions, ports, and bounded retries while keeping external network access denied.
- [ ] **W10D05 — Run guided and unguided development slices.** Use subtask scores for diagnosis, never as hidden hints in the unguided condition.
- [ ] **W10D06 — Measure transfer.** Identify which CyberGym improvements generalize, which overfit, and which new tools earn inclusion.

### Week 11 — CVE-Bench and controlled web vulnerability verification

- [ ] **W11D01 — Map the CVE-Bench contract and risk.** Select a small local development slice, document goal verifiers, and prove no target is reachable outside the benchmark network.
- [ ] **W11D02 — Add typed HTTP and browser-state tools.** Bound hosts, methods, payload sizes, redirects, cookies, authentication state, and response capture.
- [ ] **W11D03 — Model identities and state changes.** Track users, roles, objects, preconditions, actions, and rollback for authorization and data-integrity cases.
- [ ] **W11D04 — Turn claims into verifier evidence.** Require a minimal reproducible sequence and distinguish successful access from error pages or unrelated side effects.
- [ ] **W11D05 — Add controlled black-box exploration.** Bound endpoint discovery and parameter variation; forbid internet targets and unconstrained scanning.
- [ ] **W11D06 — Run a locked CVE-Bench slice.** Report pass@1, attempts, time, cost, safety events, and failure categories without publishing weaponized material.

### Week 12 — Defensive patching with BountyBench and CRSBench

- [ ] **W12D01 — Start with patch-only contracts.** Inspect BountyBench Patch and CRSBench inputs, PoVs, invariants, hidden checks, output diffs, and official evaluators.
- [ ] **W12D02 — Add transactional editing.** Produce a bounded diff, preserve the original tree, reject out-of-scope changes, and make rollback automatic.
- [ ] **W12D03 — Localize root cause from a PoV.** Trace input to fault, state the violated invariant, and distinguish a root fix from a crash-frame guard.
- [ ] **W12D04 — Verify security and functionality.** Re-run the PoV, project tests, lint/build checks, and benchmark invariants in clean containers.
- [ ] **W12D05 — Review patch quality.** Score minimality, scope, root-cause coverage, compatibility risk, test additions, and suspicious evaluator-specific workarounds.
- [ ] **W12D06 — Run patching comparisons.** Evaluate the same agent core through both adapters and publish behavioral success separately from qualitative review.

### Week 13 — CyberGym-E2E: discover, prove, fix

- [ ] **W13D01 — Implement the staged output contract.** Produce `poc.bin` and `fix.patch` and preserve the four independent evaluator stages.
- [ ] **W13D02 — Establish a patch-only baseline.** Measure repair when the PoC and crash log are provided before attempting open-ended discovery.
- [ ] **W13D03 — Add open-ended discovery.** Combine repository mapping, deterministic analyzers, harness discovery, and bounded fuzzing to find candidate crashes.
- [ ] **W13D04 — Couple evidence without coupling errors.** Ensure the patch addresses the root cause demonstrated by the PoC and record when it fixes a different valid vulnerability.
- [ ] **W13D05 — Iterate across all stages.** Use S1–S4 results to classify discovery, repair, regression, and target-mismatch failures without gaming the tests.
- [ ] **W13D06 — Run the end-to-end checkpoint.** Publish patch-only and end-to-end scores, cost curves, alternative-vulnerability cases, and patch-review findings.

**Milestone:** one agent core works through adapters on vulnerability reproduction, CTF, web-CVE, patch-only, and full discover–prove–fix tasks.

---

## Phase 4 — Scale, compare with successful systems, and publish

### Week 14 — Learn from production cyber reasoning systems

- [ ] **W14D01 — Reproduce an open reference baseline.** Run one official CyberGym example agent or EnIGMA/OpenHands configuration on the same smoke tasks and normalize budgets.
- [ ] **W14D02 — Study AIxCC architectures.** Trace how Atlantis, Buttercup, and other released systems combine fuzzing, static analysis, deduplication, LLMs, patching, and scheduling.
- [ ] **W14D03 — Add analyzer adapters.** Normalize compiler, sanitizer, coverage, static-analysis, and fuzzer evidence while preserving raw provenance.
- [ ] **W14D04 — Add specialization only where measured.** Compare a single agent with bounded specialist roles for localization, PoC generation, patching, and review.
- [ ] **W14D05 — Schedule experiments at scale.** Add quotas, queues, cache policy, image lifecycle, failure recovery, and cost caps without changing evaluator semantics.
- [ ] **W14D06 — Publish a Pareto comparison.** Compare B0, Agent v1, the cross-benchmark agent, and one reference system on success, cost, latency, safety, and complexity.

### Week 15 — Cross-benchmark capstone evaluation

- [ ] **W15D01 — Freeze the release candidate.** Pin code, prompts, models, dependencies, benchmark commits, manifests, images, budgets, and safety policy.
- [ ] **W15D02 — Run deterministic and adversarial gates.** Execute unit, adapter, replay, isolation, injection, leakage, and evaluator-integrity suites from a clean environment.
- [ ] **W15D03 — Run the locked benchmark matrix.** Evaluate CyberGym, Cybench, the controlled CVE-Bench slice, patching suites, and CyberGym-E2E without mid-run tuning.
- [ ] **W15D04 — Perform final ablations.** Remove memory, retrieval, dynamic tools, analyzers, branching, and critics one at a time to identify actual contributors.
- [ ] **W15D05 — Analyze failures by capability.** Separate localization, environment, synthesis, execution, repair, regression, policy, budget, and infrastructure failures.
- [ ] **W15D06 — Produce the technical report.** Include methodology, confidence intervals where meaningful, cost, negative results, contamination risks, safety boundaries, and sanitized traces.

### Week 16 — Package the work for research and employment

- [ ] **W16D01 — Make one-command smoke reproduction work.** Validate a clean install, fake-model tests, and a small official benchmark task with documented storage and runtime expectations.
- [ ] **W16D02 — Write the architecture and threat model.** Explain core versus adapters, evaluator authority, isolation, data flow, failure recovery, and rejected alternatives.
- [ ] **W16D03 — Build an evidence-led project page.** Lead with benchmark results and ablations, then show representative traces, patch examples, costs, and limitations.
- [ ] **W16D04 — Prepare a live demonstration.** Rehearse one safe task from task load through official evaluation, including a failed attempt and diagnostic trace.
- [ ] **W16D05 — Conduct design and incident interviews.** Defend choices, diagnose an injected regression, discuss benchmark validity, and explain how the agent could fail dangerously.
- [ ] **W16D06 — Freeze the portfolio release.** Tag the code and course artifacts, publish reproducibility instructions, archive manifests/results, and define the next research hypothesis.

**Final milestone:** a reproducible, benchmark-driven cybersecurity agent project with official evaluator evidence, cross-benchmark transfer, controlled defensive patching, safety testing, and honest cost/quality trade-offs.

## Graduation criteria

The course is complete when the repository contains:

- one reviewed and merged PR for every lesson completed under the PR-learning format, with links and merge commits recorded in the course progress log;
- a tested minimal B0 harness and an evolved agent that still shares the same small core;
- official adapters for every benchmark claimed in the report;
- at least one CyberGym locked evaluation and one CyberGym-E2E staged evaluation;
- measured transfer to Cybench plus controlled web-CVE and patching slices;
- frozen manifests, complete redacted traces, artifact hashes, model/cost accounting, and failure labels;
- ablations demonstrating which capabilities mattered;
- tests proving task/evaluator isolation, path/process/network bounds, prompt-injection handling, and leakage controls;
- a comparison with at least one runnable open reference agent;
- a technical report that clearly separates observed facts, inferred causes, and unsupported hypotheses.

## Primary references

- [CyberGym site, leaderboard, paper, and task definition](https://www.cybergym.io/cybergym/)
- [CyberGym implementation and official setup](https://github.com/sunblaze-ucb/cybergym)
- [CyberGym dataset](https://huggingface.co/datasets/sunblaze-ucb/cybergym)
- [CyberGym submission rules](https://github.com/sunblaze-ucb/cybergym/blob/main/SUBMISSION.md)
- [CyberGym benchmark-integrity FAQ](https://github.com/sunblaze-ucb/cybergym/blob/main/FAQ.md)
- [CyberGym-E2E](https://github.com/sunblaze-ucb/cybergym-e2e)
- [Cybench](https://github.com/andyzorigin/cybench)
- [CVE-Bench](https://github.com/uiuc-kang-lab/cve-bench)
- [BountyBench](https://github.com/bountybench/bountybench)
- [Microsoft ACESEvals / SABER](https://github.com/microsoft/ACESEvals)
- [AIxCC competition archive](https://archive.aicyberchallenge.com/)

These projects evolve. At the start of each benchmark week, check the upstream README and changelog, pin a revision, and record deviations in the experiment manifest.
