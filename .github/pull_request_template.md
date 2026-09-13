## Summary

Describe the project capability, defect, experiment, or documentation change.

## Motivation

Identify the benchmark requirement, observed failure, engineering risk, or
measurement that motivates this change.

## Changes

- Main implementation change.
- Tests, fixtures, adapter, or documentation changes.
- Artifact or experiment record, when applicable.

## Validation

| Check | Result |
| --- | --- |
| Unit / integration / lint / smoke | |

For benchmark runs, include the pinned benchmark revision, manifest/model
settings, runtime/cost budget, artifact hashes, and official evaluator result.
Keep setup failures separate from agent failures and never present mock output
as benchmark evidence.

## Security and benchmark integrity

- [ ] Execution stayed inside an authorized fixture or official benchmark.
- [ ] Network and evaluator boundaries were verified.
- [ ] The diff contains no credentials, benchmark archives, Docker layers,
      PoCs, hidden/fixed-side data, evaluator databases, or sensitive traces.
- [ ] Leakage, contamination, and untrusted-input risks are documented.

## Reviewer focus

Call out the invariants, trade-offs, failure paths, and evidence that deserve
the closest review.

## Out of scope

List deliberately deferred work so the change boundary remains explicit.
