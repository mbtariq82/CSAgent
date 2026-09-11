# Lesson 006 — Make the Program Boundaries Import-Safe

**Syllabus position:** W01D06  
**Expected time:** 90–120 minutes  
**Starting rule:** Do not run the full training program and do not overwrite `model.pth`. The evaluation smoke test may read the existing checkpoint.

## Outcome

By the end of this lesson:

- importing `train` or `main` performs no training, evaluation, printing, downloads, or checkpoint writes;
- training and evaluation each have an explicit reusable calculation boundary and an explicit program boundary;
- training and evaluation smoke tests exercise real project components on small datasets;
- every fast foundation check can be run with one short command sequence;
- the existing checkpoint is unchanged;
- a clean `security_agent` package exists for Lesson 7.

This closes the FashionMNIST foundation. The same separation will be used in the defensive security agent: reusable services will calculate results, while model, tool, storage, API, and command-line boundaries will construct dependencies and report them.

## Part 1 — Finish the metric contracts

`evaluate` now returns exactly:

```python
{
    "loss": mean_loss,
    "accuracy": accuracy,
    "examples": total_examples,
}
```

Make the training result follow the same rule. In `train_one_epoch`, remove `device` from the returned dictionary so that it returns exactly:

```python
{
    "loss": mean_loss,
    "examples": total_examples,
}
```

`device` controls execution; it is not a measured result. Keep it as an argument to the reusable function, but do not expose it as a metric.

Update `smoke_test_training.py` to assert the complete public contract:

```python
assert set(metrics) == {"loss", "examples"}
```

Also pass `reduction="mean"` explicitly when constructing its loss function. A smoke test should state the contract it is verifying rather than depend on a default silently.

## Part 2 — Give evaluation an explicit program boundary

`main.py` currently constructs its configuration, dataset, dataloader, model, and metrics at module scope. That means `import main` runs the complete 10,000-example evaluation.

Refactor it into these boundaries:

```python
def load_checkpoint_model(config, device):
    """Load and return the configured model on device."""
    # Construct NeuralNetwork.
    # Load config.checkpoint_path with weights_only=True and map_location=device.
    # Return the model.


def evaluate_checkpoint(config, dataloader):
    """Evaluate the configured checkpoint on an existing dataloader."""
    # Resolve device.
    # Load the model.
    # Construct a mean-reduction loss.
    # Return evaluate(...).


def run_evaluation(config):
    """Construct the complete test-data workflow and return its metrics."""
    # Construct the complete FashionMNIST test dataset.
    # Construct its non-shuffled dataloader.
    # Return evaluate_checkpoint(config, dataloader).


def main():
    """Run and report the full checkpoint evaluation."""
    metrics = run_evaluation(ExperimentConfig())
    print(f"examples={metrics['examples']}")
    print(f"eval_loss={metrics['loss']:.6f}")
    print(f"eval_accuracy={metrics['accuracy']:.2%}")


if __name__ == "__main__":
    main()
```

Keep these responsibilities separate:

```text
evaluate                    calculates metrics from supplied dependencies
evaluate_checkpoint         loads the configured model and evaluates a supplied loader
run_evaluation              constructs the real test-data workflow
main                        formats output for a person
```

Do not put printing into `evaluate` or `evaluate_checkpoint`.

## Part 3 — Give training the matching entry point

`train.py` is already safe to import because its executable code is guarded. Finish the matching structure by moving the guarded statements into `main`:

```python
def main():
    """Train, save, and report the configured model."""
    config = ExperimentConfig()
    model = run_training(config)
    torch.save(model.state_dict(), config.checkpoint_path)
    print(f"checkpoint_saved={config.checkpoint_path}")


if __name__ == "__main__":
    main()
```

Do not run this function during the lesson. The training smoke test is sufficient and must not save a checkpoint.

## Part 4 — Add a real evaluation smoke test

Create `smoke_test_evaluation.py`. It should use the real dataset, dataloader, model class, checkpoint loader, loss construction, and evaluator, but only 128 test examples.

Use this structure:

```python
import hashlib
import math

from torch.utils.data import Subset

from config import ExperimentConfig
from data import create_dataloader, create_fashion_mnist_dataset
from main import evaluate_checkpoint


def checkpoint_signature(path):
    """Return checkpoint metadata and content hash."""
    stat = path.stat()
    return (
        stat.st_mtime_ns,
        stat.st_size,
        hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def main():
    config = ExperimentConfig()
    checkpoint_before = checkpoint_signature(config.checkpoint_path)

    dataset = create_fashion_mnist_dataset(
        config.data_path,
        train=False,
        download=False,
    )
    small_dataset = Subset(dataset, range(128))
    dataloader = create_dataloader(
        small_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
    )

    metrics = evaluate_checkpoint(config, dataloader)

    assert set(metrics) == {"loss", "accuracy", "examples"}
    assert metrics["examples"] == 128
    assert isinstance(metrics["loss"], float)
    assert math.isfinite(metrics["loss"])
    assert isinstance(metrics["accuracy"], float)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert checkpoint_signature(config.checkpoint_path) == checkpoint_before


if __name__ == "__main__":
    main()
```

`download=False` is deliberate. Fast local smoke tests should not silently depend on the network. The dataset was downloaded in earlier lessons; if it is missing, the failure should tell you that the local prerequisite is absent.

## Part 5 — Tighten the training smoke test

Keep the existing 128-example parameter-change test, with these small improvements:

1. Wrap its executable body in `main()` and call it through a main guard.
2. Request the training split with `download=False`.
3. Pass `config.num_workers` to `create_dataloader`.
4. Pass `reduction="mean"` to `config.get_loss_func`.
5. Assert the exact training metric keys.
6. Keep the checkpoint signature comparison.

The training and evaluation smoke tests now prove different behaviours:

```text
training smoke test     parameters change; checkpoint does not
evaluation smoke test   metrics are valid; checkpoint does not
```

## Part 6 — Prove the imports are quiet

Compile and run the deterministic tests first:

```powershell
.\venv\Scripts\python.exe -m py_compile config.py data.py model.py optimizer.py train.py evaluate.py main.py test_evaluate.py smoke_test_training.py smoke_test_evaluation.py
.\venv\Scripts\python.exe test_evaluate.py
.\venv\Scripts\python.exe smoke_test_training.py
.\venv\Scripts\python.exe smoke_test_evaluation.py
```

Then test the two program modules as imports:

```powershell
.\venv\Scripts\python.exe -c "import train, main; print('program_imports=pass')"
```

Expected output:

```text
program_imports=pass
```

There should be no epoch output, evaluation metrics, downloads, or checkpoint messages before that line.

Finally, compare the checkpoint’s timestamp, size, and SHA-256 hash with the Lesson 5 values. Do not run `train.py` merely to verify its guard.
> Should we do this by printing the checkpoint timestamp?

## Part 7 — Prepare the security-agent package

Create this empty application boundary without adding security-agent behaviour yet:

```text
security_agent/
    __init__.py
```

Put one module docstring in `security_agent/__init__.py`:

```python
"""Defensive code security agent application."""
```

Do not move the FashionMNIST files into this package. They are the completed foundation exercise; the security agent will grow independently behind its own interfaces.

## Completion evidence

Record:

```text
py_compile=
test_evaluate=
training_smoke=
evaluation_smoke=
program_imports_output=
checkpoint_unchanged=
security_agent_package=
```

## Definition of done

Lesson 6 is complete when:

- training returns only numeric `loss` and `examples` metrics;
- evaluation returns only numeric `loss`, `accuracy`, and `examples` metrics;
- `main.py` performs no work when imported;
- `train.py` performs no work when imported;
- both executable modules use explicit `main()` functions and main guards;
- both 128-example smoke tests pass without downloading data;
- the deterministic evaluation tests still pass;
- the existing checkpoint timestamp, size, and SHA-256 remain unchanged;
- `security_agent/__init__.py` exists and contains no application behaviour.

## Next lesson

Lesson 7 begins the benchmark-driven security agent. You will pin UC Berkeley's official CyberGym, generate one Level 1 task from the official subset, send a harmless dummy PoC through the private local evaluator, and record the real task and scoring contract before designing agent abstractions.
