# Pull-Request Learning Workflow

## Learning model

Every unfinished lesson is delivered as one focused pull request. The assistant writes the implementation, tests it, records the evidence, and opens the PR. The learner studies the lesson by reviewing the diff, running or inspecting the checks, questioning decisions, and requesting changes.

The PR is the lesson. A separate long coding exercise for the learner is not required.

Completed Lessons 001–006 remain historical work unless the learner explicitly asks to recreate them as review PRs. Beginning with W02D01, every syllabus checkbox maps to exactly one PR.

## Roles

### Assistant/implementer

- Start from the merged result of the previous lesson.
- Create a lesson branch and implement only that lesson's scope.
- Add or update tests, fixtures, documentation, and reproducibility evidence.
- Run proportionate checks and report their exact results.
- Keep generated benchmark data, PoCs, secrets, and sensitive raw traces out of Git.
- Open a draft PR while work or expensive evaluation is still running; mark it ready only when the lesson contract is satisfied.
- Explain important choices and identify the most educational parts of the diff.
- Respond to review comments and push revisions to the same branch and PR.
- Never merge or close the PR unless the learner explicitly asks.
- Do not begin the next lesson until the current PR is approved and merged, unless the learner explicitly requests parallel work.

### Learner/reviewer

- Read the PR overview and review the files in the recommended order.
- Inspect the implementation and tests rather than reproducing the code by hand.
- Challenge assumptions, boundaries, security controls, naming, and experiment validity.
- Ask why an approach was chosen and what alternatives were rejected.
- Run checks locally when useful, especially for security boundaries or benchmark behavior that CI cannot reproduce.
- Request changes or approve the lesson.
- Merge the PR when satisfied.

The learner can propose code, but writing code is optional. Understanding and defending the diff is the learning objective.

## One-time repository prerequisite

PR delivery requires:

- a Git repository with an initial baseline commit;
- a GitHub remote the assistant can push to using the user's existing authenticated tooling;
- a default branch with branch protection appropriate to the learner's preferred workflow;
- CI configured without exposing model-provider, benchmark, or evaluator credentials to untrusted code.

The current workspace was not a Git repository when this workflow was introduced. Repository initialization and publishing are a one-time setup task, not silently implied permission to create a public repository. The learner must choose the destination and visibility before the first lesson PR is opened.

## Branch, commit, and PR naming

Use stable lesson identifiers:

```text
branch: course/w02d01-cybergym-contract
PR:     [W02D01] Run the CyberGym contract end to end
label:  course-lesson
```

Prefer a short sequence of meaningful commits when it helps reveal the implementation story, for example:

```text
test: define the task-generation evidence contract
feat: add CyberGym environment preflight
docs: record the private evaluator boundary
```

The final PR must be reviewable as a coherent whole. Do not leave deliberately broken code in the final diff merely to simulate an exercise.

## Required PR body

Every lesson PR uses this structure:

```markdown
## Lesson outcome

What capability or evidence exists after this PR.

## Why this lesson exists

The baseline failure, benchmark requirement, or engineering risk that motivates it.

## What changed

Concise implementation summary with links to important files and lines.

## Review route

1. First file/decision to inspect and why.
2. Second file/decision to inspect and why.
3. Tests or artifacts that demonstrate the behavior.

## Decisions and alternatives

- Decision made, evidence, and trade-off.
- Plausible alternative and why it was deferred or rejected.

## Evidence

- Exact checks and results.
- Benchmark task/manifest and official evaluator result when applicable.
- Cost, runtime, artifact hashes, or failure class when applicable.

## Security and benchmark integrity

- Isolation and network state.
- Data intentionally excluded from Git.
- Leakage/contamination considerations.
- Credentials used by location/type only, never by value.

## Reviewer questions

Two to five questions that test understanding of the important choices. These are discussion prompts, not homework requiring new code.

## Out of scope

Capabilities intentionally left for a later lesson.

## Definition of done

Checklist copied or adapted from the lesson.
```

## Review design

The implementation should teach through the diff:

- Keep the lesson focused on one primary idea.
- Put invariants in tests so the reviewer can see the intended behavior precisely.
- Prefer small named interfaces over large framework configuration.
- Include at least one negative or failure-path test when the lesson introduces a boundary.
- Link claims in the PR body to code, tests, or evaluator evidence.
- Mark generated or mechanical changes clearly and keep them separate from reasoning-heavy changes.
- Explain a surprising non-change when it is educational, such as why a framework, database, or additional tool was not added.

For an experiment lesson, the diff must include or link the frozen hypothesis and manifest. The PR should state whether the treatment was kept or rejected; a negative result can be a successful lesson.

## Evidence and CI

Fast deterministic checks should run in CI whenever possible:

- unit and contract tests;
- fake-model agent-loop tests;
- adapter tests with local fixtures;
- lint, type, serialization, replay, and policy checks;
- tests that do not require a paid model or large benchmark image.

Large downloads, real-model calls, Docker-heavy benchmark runs, and secret-bearing provider access should not be required for an ordinary external contributor's PR check. Run them in the authorized local environment and attach a sanitized summary containing pinned revisions, manifest hashes, artifact hashes, cost, and evaluator results.

Do not claim a benchmark run occurred when only a mock passed. Label evidence as `unit`, `fixture`, `smoke`, `dev`, or `locked_eval`.

## Cybersecurity artifact policy

Commit:

- source code and tests;
- synthetic, harmless fixtures;
- manifests containing public benchmark task IDs;
- hashes, aggregate results, redacted traces, and sanitized evaluator summaries;
- defensive patches for public benchmark snapshots when their license and disclosure status permit it;
- threat models, architecture records, and review notes.

Do not commit:

- model or evaluator API keys;
- `.env` files or host configuration containing secrets;
- downloaded CyberGym archives or Docker layers;
- evaluator databases, hidden tests, fixed-side images, reference PoCs, or solution stores;
- newly discovered zero-day details before coordinated disclosure;
- live-target credentials, private source, or weaponized exploit artifacts;
- raw traces containing secrets or sensitive host paths.

Use `.gitignore`, pre-commit secret checks, artifact-size checks, and a staged-diff review before every push. A GitHub PR is an external disclosure boundary even when a repository is currently private.

## Lesson state machine

```text
planned
  -> implementing
  -> draft PR
  -> ready for review
  -> changes requested <-> ready for review
  -> approved
  -> merged
  -> next lesson
```

If implementation is blocked, keep the PR in draft and describe the concrete blocker. A draft with only a plan is not a completed lesson.

## Completion rule

A lesson checkbox changes to complete only when:

- its PR is ready for review and satisfies the lesson definition of done;
- required evidence is present and accurately labeled;
- learner review questions have been discussed;
- requested changes are resolved;
- the learner approves and merges the PR.

After merge, record the PR link, merge commit, and key result in the course progress log. Then branch the next lesson from the updated default branch.
