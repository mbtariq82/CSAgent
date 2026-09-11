---
name: Course lesson
about: One reviewed implementation lesson
---

# [WXXDXX] Lesson title

## Lesson outcome

State the capability or evidence that exists after this PR.

## Why this lesson exists

Identify the baseline failure, benchmark requirement, or engineering risk that motivates the work.

## What changed

- Change with a link to the important file or line.
- Test, fixture, adapter, or documentation change.
- Artifact or experiment record, if applicable.

## Review route

1. Start with the contract or test that defines the behavior.
2. Review the implementation and its main boundary.
3. Inspect the failure path, security control, or evaluator evidence.

## Decisions and alternatives

- **Decision:** What was chosen, the evidence, and the trade-off.
- **Alternative:** What was deferred or rejected and why.

## Evidence

| Evidence class | Command/run | Result |
| --- | --- | --- |
| unit / fixture / smoke / dev / locked_eval |  |  |

Include benchmark revision, manifest hash, model/settings, cost, runtime, artifact hashes, and official evaluator result when applicable. Never present a mock result as a benchmark result.

## Security and benchmark integrity

- [ ] Task execution stayed inside the authorized fixture or benchmark environment.
- [ ] Network and evaluator boundaries were verified and documented.
- [ ] No secrets, `.env` files, benchmark archives, Docker layers, PoCs, hidden/fixed-side data, evaluator databases, or sensitive raw traces are in the diff.
- [ ] Staged changes were reviewed for credentials and sensitive artifacts.
- [ ] Leakage and contamination risks are described.

## Reviewer questions

1. Question about the lesson's most important boundary or invariant.
2. Question about the chosen trade-off.
3. Question about what the evidence proves—and what it does not prove.

## Out of scope

- Capability intentionally left for a later lesson.

## Definition of done

- [ ] The lesson's functional contract is implemented.
- [ ] Required positive and negative-path tests pass.
- [ ] Evidence is reproducible and accurately labeled.
- [ ] Documentation and review links are current.
- [ ] Requested review changes are resolved.
- [ ] The learner has approved the PR.

## After merge

- [ ] Record the PR URL and merge commit in `syllabus/PROGRESS.md`.
- [ ] Update the syllabus checkbox in the appropriate follow-up or merge commit.
- [ ] Branch the next lesson from the updated default branch.
