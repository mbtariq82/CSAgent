# Benchmark-Driven Cybersecurity Agent

This workspace now follows a benchmark-first course: begin with the smallest viable agent on **UC Berkeley CyberGym Level 1**, measure it through the official evaluator, and add capabilities only when controlled experiments justify them.

## Course documents

- [Full 16-week syllabus](syllabus/SYLLABUS.md)
- [Pull-request learning workflow](syllabus/PR_LEARNING_WORKFLOW.md)
- [Course progress and PR ledger](syllabus/PROGRESS.md)
- [Lesson 007: begin with the CyberGym contract](syllabus/LESSON_007.md)
- [Benchmarks and existing successful agents](syllabus/BENCHMARKS_AND_AGENTS.md)

Lessons 001–006 and the FashionMNIST code remain as the completed Python/ML engineering foundation. The current `security_agent/domain.py` and provider remnants are incomplete pre-redesign scratch work; Lesson 008 will replace premature product-domain abstractions with the small cross-benchmark contracts required by baseline B0.

## Benchmark progression

```text
CyberGym Level 1
    -> Cybench
    -> CVE-Bench
    -> BountyBench / CRSBench
    -> CyberGym-E2E
```

The core architecture is one agent plus benchmark adapters. LangGraph, multi-agent workflows, retrieval, long-term memory, services, and other infrastructure are optional treatments to evaluate—not assumed requirements.

## How lessons work

For every unfinished lesson, the assistant implements the lesson on a dedicated branch and opens one focused pull request. The PR contains the working change, tests or official evaluator evidence, a recommended review route, key decisions and alternatives, security notes, reviewer questions, and explicit non-goals.

The learner reviews the implementation rather than writing it by hand, requests revisions on the same PR, and approves and merges when the lesson is understood and its evidence is convincing. The next lesson starts from that merged result. The assistant does not merge a lesson PR without an explicit request.

## Safety boundary

Run only official benchmark tasks, synthetic fixtures, or explicitly authorized systems. Keep task execution isolated, deny public-network access by default, keep evaluators private and outside agent control, and never expose CyberGym's submission server to the public internet.
