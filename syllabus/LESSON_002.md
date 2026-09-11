# Lesson 002 — Make the Experiment Configurable

**Syllabus position:** W01D02  
**Expected time:** 90–120 minutes  
**Prerequisite:** Complete every item in `LESSON_001_REVIEW.md` before changing configuration.

## Why this lesson matters

The current experiment spreads important decisions across several files. Batch size is in `config.py`, while learning rate, epoch count, device selection, and checkpoint path are embedded elsewhere. This makes experiments difficult to reproduce and makes unintended differences hard to spot.

Today's goal is to create one explicit configuration and use it consistently without changing model behaviour.

## Learning objectives

By the end of this lesson, you should be able to:

1. Distinguish model parameters, hyperparameters, runtime settings, and measured metrics.
2. Explain why duplicated configuration values are dangerous.
3. Represent one experiment's settings in a typed structure.
4. Select CPU, CUDA, or automatic device resolution deliberately.
5. Refactor configuration without changing the measured result.

## Part 1 — Classify the experiment's values

Before editing code, classify each item:

| Item | Model parameter, hyperparameter, runtime setting, artifact path, or metric? |
|---|---|
| First linear layer weights | | Model parameter
| Batch size | | Model parameter
| Learning rate | | Model parameter
| Epoch count | | Model parameter
| Random seed | | Model parameter
| Requested device | | runtime setting
| Checkpoint filename | | artifact path
| Test accuracy | | metric
| Test loss | | metric

Write one sentence explaining the difference between a model parameter and a hyperparameter.
Model parameters are weights in the neural network, hyperparamaters are config values

## Part 2 — Design the configuration

Replace the single loose `BATCH_SIZE` constant with one typed configuration object. A frozen dataclass is a suitable design target:

```python
@dataclass(frozen=True)
class ExperimentConfig:
    seed: int
    batch_size: int
    epochs: int
    learning_rate: float
    checkpoint_path: Path
    requested_device: str
```

Create one default instance for the current FashionMNIST experiment.

Suggested starting values:

```text
seed=42
batch_size=64
epochs=5
learning_rate=0.001
checkpoint_path=model.pth
requested_device=auto
```

The five-epoch value describes the next training experiment; do not run that training experiment today.

Add validation in `__post_init__` or in a separate validation function. Reject at least:

- nonpositive batch size
- nonpositive epoch count
- nonpositive learning rate
- unsupported device requests

Do not create an overly general configuration framework. The objective is clarity, not abstraction for its own sake.

## Part 3 — Resolve the device explicitly

Implement one small function that converts the requested device into a `torch.device`:

```text
auto  -> CUDA when available, otherwise CPU
cpu   -> CPU
cuda  -> CUDA, but raise a clear error when unavailable
```

Questions to answer before implementation:

1. Why is silently falling back to CPU potentially undesirable when the user explicitly requested CUDA? the training/inference will take much longer
2. Why should the device be resolved once and then passed to training and evaluation? to avoid using different devices for training and evaluation
3. Why is `torch.device` preferable to repeatedly comparing arbitrary strings throughout the program? 

The current environment should resolve `auto` to CPU.

## Part 4 — Remove duplicated settings

Update `main.py`, `training.py`, and `evaluate.py` so that:

- Dataloaders use the configured batch size.
- The optimizer uses the configured learning rate.
- The outer training loop uses the configured epoch count.
- Checkpoint saving and loading use the configured path.
- Training and evaluation receive the same resolved device.
- Checkpoint loading supplies `map_location=device`.

Avoid importing isolated constants such as `BATCH_SIZE`. Import the configuration object or pass the needed values through function arguments.

This is a behaviour-preserving refactor for evaluation. Do not run `training.py`, because doing so would overwrite the checkpoint and make the comparison invalid.

## Part 5 — Verify that configuration did not change evaluation

Run a syntax check over the project files, then run `main.py` twice.

The current checkpoint should remain close to:

```text
device=cpu
examples=10000
test_loss=2.160762
test_accuracy=39.3100%
```

If the result changes after a configuration-only refactor, stop and identify the behavioural change. Do not accept a new result merely because the program runs.

Also exercise the device resolver directly:

- `auto` should return CPU on this machine.
- `cpu` should return CPU.
- `cuda` should raise the clear error you designed.
- an invalid value such as `gpu-fast` should fail validation.

## Part 6 — Record the experiment contract

At the bottom of this file, record the resolved configuration in a stable form:

```text
seed=
batch_size=
epochs=
learning_rate=
checkpoint_path=
requested_device=
resolved_device=
```

Then answer:

1. Which of these values can affect learned weights? 
2. Which can affect only runtime location or artifact storage? checkpoint_path
3. Why does making a seed configurable not yet make the program deterministic? because the weights will change if we carry on training
4. Why should a checkpoint record the configuration used to create it? for reproducability

## Optional stretch task

Add a method that serializes the configuration to plain Python values suitable for storing in a future checkpoint. Do not add a third-party configuration library.

## Definition of done

Lesson 002 is complete when:

- A typed configuration contains seed, batch size, epochs, learning rate, checkpoint path, and requested device.
- Invalid values are rejected with meaningful errors.
- Device resolution correctly handles `auto`, `cpu`, `cuda`, and invalid requests.
- Training and evaluation no longer contain duplicated configuration literals.
- Evaluation metrics remain approximately 39.31% and 2.160762.
- The checkpoint has not been overwritten during the lesson.
- The experiment contract and four written answers are complete.

## Next lesson

Lesson 003 will extract FashionMNIST dataset and dataloader construction into reusable functions and introduce the distinct responsibilities of training, validation, and test data.

