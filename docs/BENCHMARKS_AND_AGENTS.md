# Cybersecurity Benchmarks and Existing Agents

**Research snapshot:** 2026-09-11. Leaderboards and repositories change; follow the live links and pin a revision before reproducing a result.

## Start here

The similarly named `hacker-gpt/cybergym` project is a rebranded OWASP Juice Shop training application. It is **not** the benchmark used by this project. This project targets UC Berkeley's 1,507-task CyberGym:

- [CyberGym benchmark and live leaderboard](https://www.cybergym.io/cybergym/)
- [Official CyberGym code](https://github.com/sunblaze-ucb/cybergym)
- [Official dataset](https://huggingface.co/datasets/sunblaze-ucb/cybergym)
- [Official example-agent integrations](https://github.com/sunblaze-ucb/cybergym-agent-examples)
- [Submission rules](https://github.com/sunblaze-ucb/cybergym/blob/main/SUBMISSION.md)
- [Integrity, network, and scoring FAQ](https://github.com/sunblaze-ucb/cybergym/blob/main/FAQ.md)

CyberGym Level 1 gives the agent a vulnerability description and the pre-patch repository. A valid final PoC must trigger the vulnerable build but not the hidden patched build. The official repository provides a ten-task subset and example integrations for Cybench, EnIGMA, Codex, and OpenHands.

## Benchmarks to target

| Benchmark | Task and evaluator | Role in this project | Upstream |
| --- | --- | --- | --- |
| CyberGym Level 1 | Description + pre-patch source → one differentially verified PoC | Best first target for code navigation, input construction, and dynamic feedback | [site](https://www.cybergym.io/cybergym/) · [code](https://github.com/sunblaze-ucb/cybergym) · [paper](https://arxiv.org/abs/2506.02548) |
| Cybench | 40 professional CTF tasks with task evaluators and optional graded subtasks | Tests broad interactive cyber problem-solving and harness transfer | [site](https://cybench.github.io/) · [code](https://github.com/andyzorigin/cybench) |
| CVE-Bench | 40 critical web CVEs with goal-specific behavioral checks | Adds local services, HTTP state, identities, and black-box verification | [code](https://github.com/uiuc-kang-lab/cve-bench) · [paper](https://arxiv.org/abs/2503.17332) |
| BountyBench | 40 real bounties across Detect, Exploit, and Patch tasks | Exercises a real vulnerability lifecycle and checks patch invariants | [code](https://github.com/bountybench/bountybench) · [paper](https://arxiv.org/abs/2505.15216) |
| CRSBench | Source + crash-triggering PoV → patch | A focused defensive patching target available through a common evaluation harness | [ACESEvals/SABER](https://github.com/microsoft/ACESEvals) |
| CyberGym-E2E | Source only → discovery + `poc.bin` + `fix.patch`, scored in four cumulative stages | The capstone: proof, repair, regression safety, and intended-root-cause repair | [site](https://www.cybergym.io/cybergym-e2e/) · [code](https://github.com/sunblaze-ucb/cybergym-e2e) |

Useful optional breadth:

- [CTI-REALM through ACESEvals](https://github.com/microsoft/ACESEvals) evaluates threat-intelligence analysis, ATT&CK mapping, and Sigma/KQL-style detection work.
- [ExploitGym](https://www.cybergym.io/exploitgym/) evaluates turning a known vulnerability and PoV into an exploit. It is a high-risk advanced track and should remain isolated from public networks.
- [AIxCC](https://archive.aicyberchallenge.com/) is an architecture study and scale target rather than an early project benchmark.

## Runnable open agents and systems

These are the best places to inspect real implementations rather than marketing descriptions.

| System | What is available | Evidence of success | What to study |
| --- | --- | --- | --- |
| [CyberGym example agents](https://github.com/sunblaze-ucb/cybergym-agent-examples) | Official integration code for Cybench, EnIGMA, Codex, and OpenHands | These are the benchmark authors' reference integrations | Task packaging, submission protocol, and the thinnest path to a comparable baseline |
| [OpenHands](https://github.com/OpenHands/OpenHands) | Full open coding-agent framework | The original CyberGym paper's strongest reported combination was OpenHands + Claude 3.7 Sonnet at 11.9%; later official runs are on the live leaderboard | General shell/code-agent loop, sandboxing, context handling, and a reproducible historical baseline |
| [EnIGMA](https://github.com/SWE-agent/SWE-agent/tree/v0.7) | CTF-focused agent built on SWE-agent; the v0.7 tree is the paper's code reference | The EnIGMA paper reports a large gain over the prior NYU CTF baseline | LM-friendly terminal/file tools, output summarization, debugger/decompiler integration, and CTF-specific feedback |
| [EnIGMA+ / Cyber-Zero](https://github.com/amazon-science/Cyber-Zero/tree/main/enigma-plus) | Updated EnIGMA-derived scaffold and trajectory format | Used for CTF-focused cybersecurity-agent training and evaluation | Trajectory storage, step efficiency, environment feedback, and modernized benchmark plumbing |
| [BountyBench agents](https://github.com/bountybench/bountybench/tree/main/agents) | Detect, exploit, patch, executor, and base-agent implementations plus prompts and workflows | The BountyBench paper reports the evaluated custom agents and coding agents across all three modes | Phase boundaries, explicit submissions, patch transactions, service reset, exploit verification, and invariant checks |
| [CAI](https://github.com/aliasrobotics/CAI) | Open offensive/defensive agent framework with tools and agent patterns | Its published work reports strong CTF and Attack/Defense results | Lightweight ReAct agents, handoffs, security tooling, and live competition workflows; treat self-reported claims as hypotheses to reproduce |
| [Atlantis](https://github.com/Team-Atlanta/aixcc-afc-atlantis) | Team Atlanta's released final AIxCC cyber reasoning system | Team Atlanta won the 2025 DARPA AI Cyber Challenge | Static/dynamic analysis pipelines, fuzzing, deduplication, patch generation, scheduling, and large-system boundaries |
| [Buttercup standalone](https://github.com/trailofbits/buttercup) | Laptop/server-oriented version of Trail of Bits' AIxCC system | Buttercup was an AIxCC finalist system; competition versions are also public | A more approachable route into hybrid fuzzing/LLM vulnerability discovery and patching |
| [AIxCC finalist archive](https://archive.aicyberchallenge.com/) | Links to the released finalist systems, including Atlantis, RoboDuck, Buttercup, and Fuzzing Brain | All are systems that reached the AIxCC final | Compare genuinely different cyber reasoning architectures instead of copying one stack |

Also useful as a high-performing general coding-agent reference: [OpenAI Codex CLI](https://github.com/openai/codex). In the BountyBench paper's reported three-attempt evaluation, Codex CLI reached 90% on Patch, while Claude Code reached 87.5%; those figures are benchmark/configuration-specific, not universal agent rankings.

## High-scoring CyberGym design writeups

The live [CyberGym leaderboard](https://www.cybergym.io/cybergym/) is the authoritative place to find current systems and its **Source** links. Many leading entries publish architecture reports but not complete runnable code. Keep that distinction explicit.

Examples worth reading from the leaderboard snapshot used for this redesign:

- [Creation (天工)](https://github.com/AntAISecurityLab/Creation) describes a phase-structured long-horizon solver, automatic `ctags` context injection, input byte maps, parameterized candidate generation, dynamic oracle feedback, crash skepticism, model escalation, and a separate final-submission judge. The public repository is a detailed report, not the harness implementation.
- [Sangfor AI](https://github.com/Sangfor-AI/cybergym-submission-sangfor-ai-v2) describes parallel hypothesis investigation, evidence-governed final acceptance, dynamic task images, and single-final-PoC scoring. This is also a results/design repository rather than a complete implementation.
- [DoGNAVY](https://deepsec.darknavy.net/blog/cybergym) publishes a CyberGym technical report linked by the leaderboard.
- [Microsoft MDASH](https://www.microsoft.com/en-us/security/blog/2026/06/17/beyond-the-benchmark-advancing-security-at-ai-speed/) describes a multi-model security system and is linked from its leaderboard submission.

Do not begin by reproducing these systems. Their large budgets, multiple models, long horizons, dynamic infrastructure, and task-time memory obscure causality. Use them after B0 to form testable hypotheses such as:

- Does injecting symbol definitions after a search reduce navigation steps?
- Does an explicit input byte map improve long-PoC tasks?
- Does a skeptical candidate review reduce `crashes_both` failures?
- Does separating exploration from final selection improve final-submission success?
- Does branching hypotheses help enough to justify its extra cost?

## Recommended reading and reproduction order

1. Run the official CyberGym dummy submission and read its FAQ and submission rules.
2. Read the four small official example-agent integrations; reproduce one on a smoke task.
3. Build and freeze this project's smaller B0 harness.
4. Inspect EnIGMA for tool ergonomics and OpenHands for a general agent/runtime boundary.
5. Inspect BountyBench's patch and executor agents when adding transactional edits and invariant checks.
6. Read the current CyberGym leaders only after the project has failure data that makes their techniques meaningful.
7. Study Atlantis and Buttercup when evaluating hybrid analysis and production-scale architecture.

## How to compare an external agent fairly

- Pin its exact revision and dependencies.
- Use the same benchmark revision, task manifest, model, reasoning setting, attempts, dynamic access, network policy, time, and cost budget as your agent.
- Apply the same final-submission rule and official evaluator.
- Keep setup failures separate from agent failures.
- Publish raw per-task outcomes and sanitized traces, not only an aggregate percentage.
- State whether the repository contains runnable code, integration glue, trajectories, or only a design/results report.
- Never infer that a model is better from a result that changed the harness, runtime access, trial count, or budget at the same time.
