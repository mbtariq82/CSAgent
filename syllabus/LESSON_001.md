# Lesson 001 — Establish a Trustworthy Baseline

**Syllabus position:** W01D01  
**Expected time:** 90–120 minutes  
**Rule for today:** Do not retrain or change the model. First learn to measure the artifact that already exists.

## Why this is the first lesson

An engineer cannot improve a system without a trustworthy starting measurement. The current `main.py` evaluates one hard-coded FashionMNIST example. One example cannot tell us whether the checkpoint is generally useful, which classes are difficult, or whether a later change helped.

Today's goal is to turn inference on one image into evaluation of the entire test set and record the baseline before changing training.

## Learning objectives

By the end of the lesson, you should be able to:

1. Trace the path from dataset to dataloader to model output.
2. Explain the difference between training, validation, testing, and single-sample inference.
3. Explain why a classifier returns logits rather than class names or probabilities.
4. Use evaluation mode and inference mode correctly.
5. Calculate dataset-level mean loss and accuracy without averaging batches incorrectly.

## Part 1 — Map the current system

Read these files in this order:

1. `config.py`
2. `neural_network.py`
3. `training.py`
4. `main.py`

On paper or in your notes, complete this flow before continuing:

```text
FashionMNIST image batch
    shape: [N, 1, 28, 28]
        ↓
Flatten
    shape: [N, 784]
        ↓
Linear layer 1
    shape: [N, 512]
        ↓
Linear layer 2
    shape: [N, 512]
        ↓
Final linear layer (logits)
    shape: [N, 10]
        ↓
Predicted class indices
    shape: [N]
```

`N` is the number of images in the current batch. It is normally 64 in this experiment, but the final test batch contains 16 images. The `1` in `[N, 1, 28, 28]` is the image's single grayscale channel. A single image obtained directly from the dataset has shape `[1, 28, 28]`; the dataloader adds the leading batch dimension.

Expected concepts to verify:

- One image has one channel and spatial dimensions 28 × 28.
- Flattening produces 784 input features.
- The final layer produces 10 logits, one per class.
- `argmax` selects the index of the largest logit.
- `CrossEntropyLoss` expects raw logits and integer class targets.

## Part 2 — Run the current inference path

Activate the existing environment and run:

```powershell
.\venv\Scripts\python.exe main.py
```

Record:

- selected device
- predicted class
- actual class
- whether that single prediction was correct

Then answer: why would either a correct or incorrect result here be insufficient to judge the model?

## Part 3 — Implement full-dataset evaluation

Replace the one-example-only evaluation behaviour in `main.py` with a function that evaluates every batch from `test_dataloader`.

Use this interface as the design target:

```python
def evaluate(dataloader, model, loss_fn, device):
    """Return mean loss, accuracy, and number of evaluated examples."""
```

Your function should:

1. Call `model.eval()`.
2. Enter `torch.inference_mode()`.
3. Move every input and target batch to the chosen device.
4. Obtain logits from the model.
5. Add batch loss using a reduction that makes dataset-level averaging unambiguous.
6. Count correct predictions with `argmax(dim=1)`.
7. Count the number of examples actually evaluated.
8. Return values rather than only printing inside the function.

Important detail: averaging per-batch mean losses can slightly misweight the final, smaller batch. One robust design is to use summed cross-entropy loss and divide once by the total number of examples.

The program's final output should have a stable form similar to:

```text
device=cpu
examples=10000
test_loss=...
test_accuracy=...%
```

Do not change the optimizer, number of epochs, architecture, checkpoint, or transforms today.

## Part 4 — Verify the result

The checkpoint inspected before this lesson produced approximately:

```text
examples=10000
test_loss=2.1508
test_accuracy=51.52%
```

Your result should be extremely close because you are loading the same weights and test data. If it is not, investigate before proceeding. Check:

- The checkpoint is loaded before evaluation.
- The test split uses `train=False`.
- Targets and predictions have matching batch dimensions.
- Correct predictions are accumulated as counts, not batch percentages.
- Loss is divided by the correct denominator.
- No training step occurs while importing another module.

## Part 5 — Write the baseline note

At the bottom of this lesson file or in a separate local study log, record:

```text
Date: 2026-08-25
Environment: Windows, Python 3.12.10, PyTorch 2.13.0+cpu, CPU execution
Checkpoint: model.pth
Parameter count: 669,706
Test examples: 10,000
Test loss: 2.160762
Test accuracy: 39.31%
What I expected: The corrected evaluator should reproduce the independently verified metrics for the current checkpoint.
What surprised me: Averaging batch means can be incorrect because the final 16-example batch would receive the same weight as a full 64-example batch.
One question I still have: How will changing the training configuration improve the model while keeping comparisons reproducible?
```

The current model contains 669,706 trainable parameters. Confirm this yourself with a parameter-count expression rather than copying the number blindly.

## Knowledge check

Answer these without searching first:

1. Why does the final layer have 10 outputs? FashionMNIST has 10 classes, so the final layer returns one logit for each possible class.
2. What is a logit? A logit is a raw, unnormalised class score. Logits may be negative and do not need to add up to one.
3. Why is softmax unnecessary before `CrossEntropyLoss`? `CrossEntropyLoss` combines a numerically stable log-softmax operation with negative log-likelihood, so it expects raw logits. Applying softmax first would be redundant and less numerically stable.
4. What does `model.eval()` change, and why is it still good practice when this model has no dropout or batch normalization? It recursively switches modules into evaluation behaviour. For example, Dropout stops randomly removing activations, and BatchNorm uses its learned running statistics instead of updating them from the current batch. This network contains neither module, so its output is currently unchanged, but calling `eval()` keeps the evaluation path correct if the architecture later changes. It does not disable gradient tracking; inference mode does that separately.
5. What does inference mode save compared with tracking gradients? It prevents PyTorch from constructing an autograd graph and removes additional autograd bookkeeping such as view tracking and version-counter updates. This reduces memory usage and execution overhead during evaluation.
6. Why must the test set remain separate from hyperparameter selection? Choosing hyperparameters from test results leaks information about the test set into model development. Keeping it separate preserves an independent, less biased estimate of how the final model generalises to unseen data. Validation data should be used for hyperparameter selection instead.
7. Why can the mean of batch means be slightly wrong? Batches can contain different numbers of examples. Averaging their means directly gives a small final batch the same influence as a full batch. Loss should be accumulated per example and divided by the total number of evaluated examples.

## Optional stretch task

Accumulate correct and total counts separately for each of the 10 FashionMNIST classes. Print a compact per-class accuracy table. Do not attempt to fix the weak classes yet; this is still observation day.

## Definition of done

Lesson 1 is complete only when:

- `main.py` evaluates all 10,000 test examples.
- Evaluation does not build autograd graphs.
- Loss and accuracy are correctly aggregated.
- The result is close to the known 51.52% baseline.
- You have recorded the baseline and answered the seven knowledge-check questions.
- You can explain the complete evaluation path without reading the code line by line.

## Next lesson

Lesson 2 will expand `config.py` and make the experiment's seed, epochs, learning rate, device, and checkpoint path explicit. Only after the experiment is controllable will we retrain the model.
