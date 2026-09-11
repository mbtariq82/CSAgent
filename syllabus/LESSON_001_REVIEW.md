# Lesson 001 Review — Revision Required

**Reviewed:** 2026-08-25  
**Status:** Final revision required  
**Next action:** Correct the returned example count and value types, then finish the written evidence before beginning Lesson 002.

## Verified result

The current `model.pth` differs from the checkpoint that originally produced 51.52% accuracy. It was modified after Lesson 001 was created. A trusted, sample-weighted evaluation of the current checkpoint produced:

```text
examples=10000
correct=3931
test_accuracy=39.3100%
test_loss=2.160762
```

This is now the correct baseline for the current checkpoint. Do not change the model or retrain it merely to reproduce the old 51.52% figure.

## What passed

- Evaluation was moved into its own `evaluate.py` module.
- The code iterates over the complete test dataloader.
- `model.eval()` is called before evaluation.
- Inputs and targets are moved to a device.
- Predictions use `argmax` along the class dimension.
- Correct predictions are accumulated as counts before accuracy is calculated.
- The files import and `main.py` executes successfully.

## Required corrections

### 1. Use inference mode

The lesson required `torch.inference_mode()`, but the implementation uses `torch.no_grad()`.

Both disable gradient recording. Inference mode additionally removes more autograd-related bookkeeping, including view tracking and version-counter updates. It is appropriate when tensors created inside the region will only be used for inference.

### 2. Return results

The documented function contract says that `evaluate` returns mean loss, accuracy, and example count. The current function only prints and therefore implicitly returns `None`.

Printing belongs at the program boundary in `main.py`. Returning values makes evaluation testable and reusable.

### 3. Weight loss by examples

The current loss function returns a mean for each batch, and the code averages those batch means. The final FashionMNIST batch contains only 16 examples while the other batches contain 64, but this calculation gives every batch equal weight.

Use a summed loss and divide once by the total number of examples, or multiply each batch mean by its batch size before accumulating it.

### 4. Pass the selected device

`main.py` selects a device but calls `evaluate(test_dataloader, model)` without passing it. The function therefore uses its default CPU value. This happens to work today because the environment is CPU-only, but it will fail when the model is moved to CUDA and the input remains on the CPU.

Make the device a required argument rather than silently defaulting it.

### 5. Return and print the example count

The required stable output includes the number of evaluated examples. Print this in `main.py` using the value returned by `evaluate`.

### 6. Preserve a written baseline record

No completed baseline-note section was found. Record the current checkpoint's date, environment, parameter count, examples, loss, accuracy, observations, and one remaining question.

### 7. Correct the tensor shapes

The written shapes omit important dimensions. Think in batches:

```text
input image batch:      [N, 1, 28, 28]
after flatten:          [N, 784]
after first linear:     [N, 512]
after second linear:    [N, 512]
logits:                 [N, 10]
predicted class index:  [N]
```

For one unbatched dataset image the shape is `[1, 28, 28]`, not merely `28 × 28`.

## Knowledge-check feedback

### 1. Why does the final layer have 10 outputs?

There are 10 mutually exclusive FashionMNIST classes, so the model emits one **logit** for each class. These outputs are not yet probabilities.

### 2. What is a logit?

In this multiclass model, a logit is a raw, unnormalized real-valued class score. Logits do not have to be positive and do not add up to one. Applying softmax converts the 10 logits into probabilities that do add up to one.

### 3. Why is softmax unnecessary before `CrossEntropyLoss`?

PyTorch cross-entropy combines a numerically stable log-softmax calculation with negative log-likelihood. Applying softmax yourself is redundant and can reduce numerical stability. Pass raw logits to the loss.

### 4. What does `model.eval()` change?

It recursively sets modules to evaluation behaviour. This matters for modules such as Dropout and BatchNorm. It does **not** disable gradient tracking. The current network has neither module, so its numbers do not change, but calling it makes the evaluation path correct if the architecture later changes.

### 5. What does inference mode save?

It prevents construction of the autograd graph and removes additional autograd bookkeeping. This reduces memory consumption and execution overhead. It is unrelated to storing a model cache.

### 6. Why keep the test set separate?

Repeatedly selecting architectures or hyperparameters using test results leaks information from the test set into the development process. The final test result then becomes an optimistically biased estimate rather than an independent measure of generalization.

### 7. Why can the mean of batch means be wrong?

If batch sizes differ, a plain mean gives a small batch the same influence as a full batch. For example, averaging the mean of 64 examples and the mean of 16 examples weights each group at 50%, rather than weighting individual examples equally.

Rewrite these answers in your own words in `LESSON_001.md`. Do not copy them without making sure you can explain them aloud.

## Reassessment checklist

Lesson 001 passes when all of the following are true:

- `evaluate` uses `torch.inference_mode()`.
- `evaluate` returns `(mean_loss, accuracy, example_count)` or an equivalently clear structure.
- Mean loss is weighted correctly per example.
- Device is a required argument and is supplied by `main.py`.
- `main.py` prints device, examples, test loss, and test accuracy in a stable format.
- Running the current checkpoint produces approximately 39.31% and 2.160762.
- The baseline note and corrected knowledge answers are present.

Do not change `model.pth` during the revision.

## Reassessment 2 — 2026-08-25

The request to keep `device` optional is accepted for now and is not counted against the lesson.

### Newly passed

- `torch.inference_mode()` is used correctly.
- Loss is accumulated with `reduction="sum"` and divided by the number of examples.
- Evaluation returns a structured result rather than only printing internally.
- The current checkpoint remains unchanged.
- The verified loss and accuracy match: `2.160762` and `39.31%`.

### Remaining implementation corrections

1. The returned `examples` field currently contains `num_batches`, which is `157`. Return `total_examples`, which is `10000`.
2. Return loss and accuracy as numeric values. Formatting them as strings inside `evaluate` makes later comparisons, tests, and calculations unnecessarily difficult. Keep accuracy as a fraction such as `0.3931` and format it as a percentage only in `main.py`.
3. Divide the correct count by `total_examples` rather than the separate dataset-size variable. They are equal in this run, but using the observed count keeps the calculation internally consistent.

A suitable result contract is conceptually:

```text
device: numeric-device description or string
examples: integer
test_loss: float
test_accuracy: float in the interval [0, 1]
```

`main.py` is responsible for presenting those raw values as readable text.

### Remaining written work

- Add the completed baseline note requested in Part 5.
- Correct the shapes in Part 1 to preserve channel and batch dimensions.
- Expand answer 4: `model.eval()` changes the behaviour of modules such as Dropout and BatchNorm; it does not itself disable gradients.
- Expand answer 5 to mention both the autograd graph and its bookkeeping/memory overhead.
- Expand answer 6 to mention test-data leakage and preservation of an unbiased final generalization estimate.
- Expand answer 7 to state that a small final batch receives the same weight as a full batch when batch means are averaged directly.

### Final target

Running `main.py` should present approximately:

```text
device=cpu
examples=10000
test_loss=2.160762
test_accuracy=39.31%
```
