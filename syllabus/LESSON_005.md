# Lesson 005 — Make Evaluation a Trustworthy Function

**Syllabus position:** W01D05  
**Expected time:** 90–120 minutes  
**Starting rule:** Do not run `train.py` and do not save a checkpoint. This lesson evaluates existing or synthetic models only.

## Outcome

By the end of this lesson, `evaluate.py` will contain one reusable function that:

- receives every runtime dependency explicitly;
- creates no dataset, model, configuration, or checkpoint itself;
- evaluates every example, including a smaller final batch;
- returns Python numbers for mean loss, accuracy, and example count;
- creates no gradients and performs no optimizer work;
- fails clearly on empty data or non-finite loss;
- is proven correct with tiny deterministic tests.

This is the same evaluation discipline we will later use for security findings, evidence quality, repository retrieval, tool calls, and agent trajectories: define the metric contract, build controlled examples, and make failures executable.

## Part 1 — Identify the current loss contract

Your current evaluator contains:

```python
test_loss += loss_fn(pred, y).item()
...
test_loss /= total_examples
```

This is correct only when `loss_fn` uses `reduction="sum"`, because each batch contributes its total loss. If the caller supplies the usual `reduction="mean"`, the code adds several batch means and then divides by the number of examples. The result becomes too small and changes when the batch size changes.

For this lesson, standardize the reusable evaluation function on this contract:

```text
loss_fn returns the mean loss for the current batch
evaluation returns the mean loss across all examples
```

Therefore use the same sample-weighted aggregation pattern as training:

```python
batch_size = targets.size(0)
total_loss += batch_loss.item() * batch_size
total_examples += batch_size
```

The smaller final batch remains in the evaluation and receives exactly the weight its sample count deserves.

## Part 2 — Refactor `evaluate`

Keep this public interface:

```python
def evaluate(dataloader, model, loss_fn, device):
    """Evaluate every example and return numeric classification metrics."""
```

Implement the following execution order:

```python
def evaluate(dataloader, model, loss_fn, device):
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_examples = 0

    with torch.inference_mode():
        for batch, (inputs, targets) in enumerate(dataloader):
            # 1. Move inputs and targets to device.
            # 2. Calculate logits.
            # 3. Calculate mean batch loss.
            # 4. Reject a non-finite loss with the batch number.
            # 5. Accumulate sample-weighted loss.
            # 6. Accumulate the number of correct predictions.
            # 7. Accumulate the number of examples.

    # Reject empty input before dividing.
    # Return the three required Python numbers.
```

Return exactly this shape:

```python
{
    "loss": mean_loss,
    "accuracy": accuracy_ratio,
    "examples": total_examples,
}
```

Metric contracts:

- `loss` is a Python `float` containing mean loss per example.
- `accuracy` is a Python `float` between `0.0` and `1.0`, not a formatted percentage.
- `examples` is a Python `int`.
- Do not return `device`; it is an execution dependency, not an evaluation result.
- Do not print inside `evaluate`; reporting belongs to the caller.

Use a clear empty-data failure such as:

```python
raise ValueError("Cannot evaluate an empty dataloader")
```

Use a clear non-finite-loss failure such as:

```python
raise RuntimeError(
    f"Non-finite evaluation loss at batch {batch}: {batch_loss.item()}"
)
```

There is no optimizer and no call to `backward()` in evaluation.

## Part 3 — Build the aggregation test first

Create `test_evaluate.py`. Use logits as the dataset inputs and `torch.nn.Identity` as the model. This removes neural-network randomness: the values supplied by the dataset become the model outputs directly.

Start with:

```python
import math

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from evaluate import evaluate


device = torch.device("cpu")
logits = torch.tensor([
    [5.0, 0.0],  # predicts class 0: correct
    [0.0, 5.0],  # predicts class 1: correct
    [2.0, 1.0],  # predicts class 0: target will be 1
])
targets = torch.tensor([0, 1, 1])

dataset = TensorDataset(logits, targets)
dataloader = DataLoader(dataset, batch_size=2, shuffle=False)
model = nn.Identity()
loss_fn = nn.CrossEntropyLoss(reduction="mean")

metrics = evaluate(dataloader, model, loss_fn, device)
expected_loss = F.cross_entropy(logits, targets, reduction="mean").item()

assert metrics["examples"] == 3
assert math.isclose(metrics["loss"], expected_loss, rel_tol=1e-6)
assert math.isclose(metrics["accuracy"], 2 / 3, rel_tol=1e-6)
assert isinstance(metrics["loss"], float)
assert isinstance(metrics["accuracy"], float)
assert isinstance(metrics["examples"], int)
```

This creates batches of sizes two and one. The incorrect final example has a much larger loss than the first two, so averaging the two batch means equally will fail the test. Only correct sample-weighted aggregation matches `expected_loss`.

Run:

```powershell
.\venv\Scripts\python.exe test_evaluate.py
```

No output with exit code zero means the assertions passed.

## Part 4 — Add the failure and gradient tests

Append three focused checks to `test_evaluate.py`.

### Empty dataloader

Create an empty dataset with the correct shapes and verify that evaluation raises `ValueError` rather than dividing by zero:

```python
empty_dataset = TensorDataset(
    torch.empty((0, 2)),
    torch.empty((0,), dtype=torch.long),
)
empty_dataloader = DataLoader(empty_dataset, batch_size=2)
```

Use `try`/`except` and fail explicitly if no exception is raised:

```python
try:
    evaluate(empty_dataloader, model, loss_fn, device)
except ValueError:
    pass
else:
    raise AssertionError("Empty evaluation data should raise ValueError")
```

### Non-finite loss

Create logits containing `NaN`, evaluate them, and verify that `RuntimeError` is raised before corrupt metrics are returned:

```python
nan_dataset = TensorDataset(
    torch.tensor([[float("nan"), 0.0]]),
    torch.tensor([0]),
)
```

### No gradients

Use a model with parameters and verify evaluation does not populate `.grad`:

```python
linear_model = nn.Linear(2, 2)

evaluate(dataloader, linear_model, loss_fn, device)

assert all(parameter.grad is None for parameter in linear_model.parameters())
assert linear_model.training is False
```

The test is checking two different mechanisms:

- `model.eval()` switches layers such as dropout and batch normalization into evaluation behaviour.
- `torch.inference_mode()` prevents autograd graph construction.

Neither mechanism replaces the other.

## Part 5 — Update the real checkpoint caller

In `main.py`, request a mean-reduction loss so the caller follows the new evaluation contract:

```python
loss_fn=config.get_loss_func(reduction="mean")
```

Update the output boundary to use stable names:

```python
metrics = evaluate(...)

print(f"examples={metrics['examples']}")
print(f"eval_loss={metrics['loss']:.6f}")
print(f"eval_accuracy={metrics['accuracy']:.2%}")
```

Do not move the dataset or checkpoint construction into `evaluate.py`. `evaluate` calculates metrics; the program boundary constructs dependencies and formats output.

`main.py` still performs work when imported. Leave that for Lesson 6, where training and evaluation entry points will receive matching smoke tests and import-safety checks.

## Part 6 — Safe verification

Run the deterministic tests first:

```powershell
.\venv\Scripts\python.exe -m py_compile evaluate.py test_evaluate.py main.py
.\venv\Scripts\python.exe test_evaluate.py
```

Verify importing the reusable module is quiet:

```powershell
.\venv\Scripts\python.exe -c "import evaluate; print('import_evaluate=pass')"
```

Expected output:

```text
import_evaluate=pass
```

Only after the deterministic tests pass, run the existing checkpoint evaluation:

```powershell
.\venv\Scripts\python.exe main.py
```

This must not modify `model.pth`. Its accuracy should remain equivalent to the Lesson 1 baseline; small formatting changes are expected, metric changes are not.

## Completion evidence

Record this short result block at the bottom of this lesson or in a local note:

```text
aggregation_test=pass
empty_loader_test=pass
non_finite_loss_test=pass
no_grad_test=pass
import_evaluate_output=import_evaluate=pass
checkpoint_unchanged=pass (timestamp, size, and SHA-256 identical)
real_eval_examples=10000
real_eval_loss=2.160762
real_eval_accuracy=39.31%
```

No written explanation is required if the code and outputs prove each item.

## Definition of done

Lesson 5 is complete when:

- `evaluate` has no hidden runtime dependencies or output side effects.
- It uses mean batch loss and sample-weighted epoch aggregation.
- It returns only numeric `loss`, `accuracy`, and `examples` metrics.
- The uneven-batch deterministic test matches full-dataset cross-entropy and `2/3` accuracy.
- Empty data and non-finite loss fail clearly.
- Evaluation creates no parameter gradients and leaves the model in evaluation mode.
- `main.py` uses mean-reduction loss and formats the returned metrics.
- Importing `evaluate` is quiet.
- The real checkpoint still evaluates over all 10,000 test examples without changing `model.pth`.

## Next lesson

Lesson 6 will finish the FashionMNIST foundation: add matching smoke tests and import-safe program boundaries for training and evaluation, then prepare a clean application directory for the defensive security agent.
