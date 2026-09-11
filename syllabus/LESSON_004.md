# Lesson 004 — Make Training Safe to Import and Test

**Syllabus position:** W01D04  
**Expected time:** 90–120 minutes  
**Starting rule:** Do not run the full five-epoch program and do not overwrite `model.pth`. Verify the refactor with import checks and a small in-memory smoke test.

## Why this lesson matters

The current `training.py` performs substantial work at module scope. Importing it constructs the dataset, dataloader, model, loss, and optimizer; starts the training loop; and saves weights. That makes the training function difficult to reuse or test and makes an innocent import capable of overwriting a checkpoint.

This becomes especially dangerous on Windows when `num_workers > 0`, because worker processes start by importing the main module. Executable work must live behind a guarded entry point.

Today's goal is to make this safe:

```python
import training
```

Importing the module should define functions only. It must not download data, train a model, print epochs, or write files.

## Learning objectives

By the end of this lesson, you should be able to:

1. Explain what Python executes during a module import.
2. Explain the purpose of `if __name__ == "__main__":`.
3. Remove global runtime dependencies from a training function.
4. Separate one epoch of optimization from whole-program orchestration.
5. Return numeric training metrics rather than relying only on console output.
6. Prove that importing the training module has no training or checkpoint side effects.

## Part 1 — Understand import-time execution

Answer before editing:

1. Which lines in the current `training.py` execute when another module imports it? every unindented line gets run, so if you want code to not run during import you can use if __name__=='__main__'
2. Why could importing `training.py` currently overwrite `model.pth`? importing training.py will also run the file as an executable which currently overwrites models.pth
3. What value does `__name__` have when a file is executed directly? '__main__'
4. What value does `__name__` have when that file is imported as a module? false
5. Why is a main guard particularly important for multiprocessing dataloaders on Windows?

Use this mental model:

```text
python training.py
    __name__ == "__main__"
    guarded program entry runs

import training
    __name__ == "training"
    functions/classes are defined
    guarded program entry does not run
```

## Part 2 — Design `train_one_epoch`

Rename or replace the current `train` function with an explicit one-epoch function:

```python
def train_one_epoch(dataloader, model, loss_fn, optimizer, device):
    """Train for one pass over dataloader and return epoch metrics."""
```

Every runtime dependency used by the function must arrive through its arguments. It must not read a global `device`, model, optimizer, loss function, dataloader, or configuration object.

The function should:

1. Call `model.train()`.
2. Initialize `total_loss` and `total_examples`.
3. Iterate over the supplied dataloader.
4. Move each input and target batch to the supplied device.
5. Clear old gradients before the forward pass.
6. Calculate logits and mean batch loss.
7. Backpropagate and update parameters.
8. Accumulate sample-weighted loss.
9. Return numeric mean loss and example count.

Use this order inside each batch:

```python
optimizer.zero_grad(set_to_none=True)
logits = model(inputs)
loss = loss_fn(logits, targets)
loss.backward()
optimizer.step()
```

Because the training loss uses `reduction="mean"`, accumulate epoch loss like this conceptually:

```text
total_loss += batch_mean_loss × batch_size
mean_epoch_loss = total_loss / total_examples
```

This prevents a smaller final batch from receiving equal weight to a full batch.

Return a simple structure containing raw numbers, for example:

```python
{
    "loss": mean_epoch_loss,
    "examples": total_examples,
}
```

Do not return formatted strings. Formatting belongs at the program boundary.

## Part 3 — Create whole-program orchestration

Create a function that owns construction and the multi-epoch loop:

```python
def run_training(config):
    """Construct training components, run all epochs, and return the trained model."""
```

Move all of this existing module-scope work inside `run_training`:

- Resolve the device.
- Construct the training dataset.
- Construct the shuffled training dataloader.
- Construct the model.
- Construct the mean-reduction training loss.
- Construct the optimizer.
- Run the configured epoch loop.

For each epoch, call `train_one_epoch` and print its returned metrics in a stable form:

```text
epoch=1
examples=60000
train_loss=...
```

The orchestration function may print progress because it represents the program workflow. The reusable `train_one_epoch` function should focus on calculation and return values.

At the end, return the trained model. Do not save it inside `train_one_epoch`.

## Part 4 — Add a guarded entry point

Create a small program entry function:

```python
def main():
    config = ExperimentConfig()
    model = run_training(config)
    torch.save(model.state_dict(), config.checkpoint_path)
    print(f"saved_checkpoint={config.checkpoint_path}")


if __name__ == "__main__":
    main()
```

This preserves direct execution:

```powershell
.\venv\Scripts\python.exe training.py
```

but prevents execution during import:

```python
import training
```

Do not run `training.py` directly during this lesson. The main guard is being verified structurally and through safe import behaviour first.

## Part 5 — Prove importing is safe

Record the last-modified time of `model.pth`, then run:

```powershell
.\venv\Scripts\python.exe -c "import training; print('import_training=pass')"
```

Expected output:

```text
import_training=pass
```

It must not print:

- Dataset download messages
- Epoch headers
- Training loss
- `Done!`
- Checkpoint-save messages

Verify that the modification time of `model.pth` did not change.

Also check that importing exposes the intended functions:

```powershell
.\venv\Scripts\python.exe -c "import training; print(callable(training.train_one_epoch)); print(callable(training.run_training))"
```

Expected:

```text
True
True
```

## Part 6 — Run a safe training smoke test

Do not call `run_training`, because it is configured for five complete epochs. Instead, write `smoke_test_training.py` that imports `train_one_epoch` and constructs a tiny workload.

Use the real FashionMNIST training dataset but wrap only the first 128 examples with `torch.utils.data.Subset`:

```python
small_dataset = Subset(training_dataset, range(128))
```

Create a dataloader for that subset, a fresh model, training loss, and optimizer. Save a clone of one parameter tensor before training:

```python
before = next(model.parameters()).detach().clone()
```

Run one call to `train_one_epoch`, then compare:

```python
after = next(model.parameters()).detach()
parameter_delta = (after - before).abs().sum().item()
```

Verify:

```text
examples=128
loss is finite and greater than zero
parameter_delta is greater than zero
model.pth modification time is unchanged
```

Protect the smoke-test script with its own main guard.

This proves that the reusable function performs optimization without running the full training program or saving a checkpoint.

## Part 7 — Check failure boundaries

Add clear guards or assertions for conditions that would make the metric calculation invalid:

- An empty dataloader must not cause division by zero without explanation.
- A non-finite loss should raise a clear error rather than silently corrupting training.

You do not need a complex recovery system. A direct `ValueError` or `RuntimeError` with useful context is sufficient.

Answer:

1. Why is silently returning a zero loss for an empty dataloader misleading? zero loss might suggest a really good model instead of missing data
2. What are some possible causes of `NaN` or infinite training loss? 
3. Why should failure detection occur before saving a new checkpoint?

## Part 8 — Record the execution contract

Complete:

```text
import_training_output=
import_changed_checkpoint=
smoke_test_examples=
smoke_test_loss=
parameter_delta=
checkpoint_changed_during_smoke_test=
```

Then complete this responsibility table:

| Component | Responsibility | Allowed side effects |
|---|---|---|
| `train_one_epoch` | | |
| `run_training` | | |
| `main` | | |
| `smoke_test_training.py` | | |

Finally, describe the execution flow in your own words:

```text
Direct execution
    → main
    → run_training
    → repeated train_one_epoch
    → save checkpoint

Import
    → define functions only
    → no training
    → no checkpoint write
```

## Optional stretch task

Create a small typed result such as a frozen `EpochMetrics` dataclass instead of returning a dictionary. Only do this if you can explain why it improves the interface; do not add abstraction merely to make the code longer.

## Definition of done

Lesson 004 is complete when:

- Importing `training` performs no dataset construction, training, printing, or checkpoint writes.
- `train_one_epoch` receives all runtime dependencies explicitly.
- `train_one_epoch` returns sample-weighted numeric epoch metrics.
- `run_training(config)` owns component construction and the epoch loop.
- Direct execution is protected by a main guard.
- The 128-example smoke test produces a finite loss and changes fresh model parameters.
- Neither import nor smoke testing changes `model.pth`.
- Empty-data and non-finite-loss failures are handled clearly.
- The execution contract, responsibility table, and three written answers are complete.

## Next lesson

Lesson 005 will apply the same separation to evaluation: a reusable metrics function, a guarded evaluation program, stable human-readable reporting, and tests for aggregation and edge cases.

