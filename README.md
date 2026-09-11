# Benchmark-Driven Cybersecurity Agent

A benchmark-first cybersecurity agent developed against official evaluators.
The project starts with the smallest viable harness for UC Berkeley CyberGym
Level 1, measures it under pinned and isolated conditions, and adds capability
only when controlled experiments justify the complexity.

## Project status

The CyberGym evaluation boundary is implemented. The repository currently
contains:

- a pinned Level 1 contract for `arvo:10400`;
- validation of the exact agent-visible file set;
- explicit classification of transport, vulnerable execution, patched
  execution, final submission, and task success;
- a metadata-only preflight and evidence recorder;
- an isolated local evaluator smoke result using a harmless four-byte artifact;
- documented environment, artifact hashes, image digests, and shutdown state.

The smoke result proves that the official task generator and local evaluator
can exchange a submission on this host. It is not an agent score and does not
prove container-to-evaluator routing; that path requires Linux or WSL2 with
Docker integration enabled.

## Project layout

```text
security_agent/
  benchmarks/
    cybergym/              Level 1 contract, helpers, runbook, and evidence
scripts/
  cybergym_baseline.py     metadata-only baseline CLI
tests/
  test_cybergym_contracts.py
docs/
  ROADMAP.md
  BENCHMARKS_AND_AGENTS.md
```

The root-level FashionMNIST files are retained as historical ML experiments;
they are outside the active cybersecurity-agent architecture. The unfinished
`security_agent/domain.py` and provider stubs are also not part of the current
baseline and will be replaced by the minimal B0 contracts described in the
roadmap.

## Development roadmap

The project follows this benchmark progression:

```text
CyberGym Level 1
    -> Cybench
    -> CVE-Bench
    -> BountyBench / CRSBench
    -> CyberGym-E2E
```

One agent core will sit behind benchmark-specific adapters. LangGraph,
multi-agent workflows, retrieval, long-term memory, and specialist roles are
candidate treatments, not assumed requirements.

- [Project roadmap](docs/ROADMAP.md)
- [Benchmarks and existing agents](docs/BENCHMARKS_AND_AGENTS.md)
- [CyberGym baseline runbook](security_agent/benchmarks/cybergym/README.md)
- [CyberGym Level 1 contract](security_agent/benchmarks/cybergym/CONTRACT.md)
- [Safety boundary](security_agent/benchmarks/cybergym/SAFETY_BOUNDARY.md)

## Development workflow

Changes are delivered through focused pull requests. Each PR should state its
motivation, implementation boundary, tests, benchmark evidence, security
impact, and explicit non-goals. Benchmark runs must pin their inputs and keep
infrastructure failures separate from agent failures. Negative results are
valid when they are reproducible and inform the next engineering decision.

## Safety boundary

Run only official benchmark tasks, synthetic fixtures, or explicitly
authorized systems. Keep task execution isolated, deny public-network access
by default, keep evaluators private and outside agent control, and never expose
CyberGym's submission server to the public internet.
