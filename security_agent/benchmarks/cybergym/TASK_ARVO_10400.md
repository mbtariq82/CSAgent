# Generated task: `arvo:10400` / Level 1

The task was generated from the official CyberGym dataset and pinned source
revision. Only the Level 1 files listed below were copied into the external
generated-task directory. The repository archive was never unpacked into this
project repository.

```text
task_id=arvo:10400
difficulty=level1
generated_task_directory=C:\Users\mbtar\cybergym_generated\arvo-10400-level1
agent_visible_files=README.md, description.txt, repo-vul.tar.gz, submit.sh
forbidden_files_present=no
fixed_side_data_present=no
reference_poc_present=no
patch_or_error_data_present=no
```

The authoritative task generator creates `submit.sh` with a task identifier,
agent identifier, and checksum. The endpoint is a local private gateway; no
credentials are committed or printed here.

## Metadata-only artifact inventory

Run this from the project repository after generating the task:

```powershell
python scripts/cybergym_baseline.py inspect-task `
  --task-dir C:\Users\mbtar\cybergym_generated\arvo-10400-level1 `
  --task-id arvo:10400 `
  --output C:\Users\mbtar\cybergym_generated\arvo-10400-level1\inventory.json
```

The resulting `inventory.json` is evidence only. It contains file names,
sizes, and SHA-256 hashes; it does not contain the PoC, source contents, or
evaluator output.

## Recorded hashes

The external source downloads were verified against the dataset's public LFS
objects before task generation:

```text
tasks.json=9cea452cc1e1a3703e0f60c2dfc8642430aab9f50433f976581509de58c7048f
description.txt=3cfbcdcdffc1026741d2ec42f1b75eb3d99e31028bddc08850a27287fba1ee19
repo-vul.tar.gz=94f56b7037a4c0976a041f9bc0d340f9ed2db72fb6ff40d859503c25b6dac380
```

## Official image digests used by the smoke evaluator

```text
n132/arvo:10400-vul=sha256:c4b1fea3df4e312e82747c54b715166f2e66654acbc480a328e20cdd8270b444
n132/arvo:10400-fix=sha256:07e595f71ae80c5e521312df9a54a08ad08cfc1a07e868c13d7360b6e6dcc394
```

The image store is external to Git. Mutable tags are shown only as the
upstream lookup names; the digests above identify the actual images pulled.
