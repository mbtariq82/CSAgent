# Lesson 003 — Build a Reusable Data Pipeline

**Syllabus position:** W01D03  
**Expected time:** 90–120 minutes  
**Starting rule:** Do not train or overwrite `model.pth`. This lesson refactors data construction and verifies that evaluation is unchanged.

## Why this lesson matters

`main.py` and `training.py` currently repeat the same FashionMNIST transform, dataset construction, and dataloader construction. Repetition is risky: if one copy changes while another does not, training and evaluation may process data differently.

Today's goal is to create one reusable data module that defines how FashionMNIST examples become batches.

## Learning objectives

By the end of this lesson, you should be able to:

1. Explain the different responsibilities of a `Dataset` and a `DataLoader`.


2. Explain when transforms are applied.


3. Explain why training data is normally shuffled but test data is not.


4. Construct train and test loaders through shared functions.
5. Verify shapes, dtypes, ranges, dataset sizes, and sampling behaviour.
6. Distinguish the roles of training, validation, and test data.

## Part 1 — Understand the data abstractions

Complete these definitions in your own words before editing code:

```text
Dataset: collection of examples and labels from pytorch
DataLoader: iterator from dataset
Transform: convert an individual example
Batch: split dataset to parallelise computation?
Sampler: ??
```

Use these ideas to check your answers:

- A dataset represents an indexed collection of individual examples and labels.
- A transform converts an individual example when the dataset retrieves it.
- A dataloader groups examples into batches and controls sampling, shuffling, workers, and iteration.
- A sampler determines which dataset indices are requested and in what order.

For the current pipeline, trace the shape transition:

```text
Stored FashionMNIST image
        ↓ transform
Single tensor: [1, 28, 28], float32, values approximately in [0, 1]
        ↓ dataloader batching
Batch tensor: [N, 1, 28, 28]
Target tensor: [N]
```

Answer:

1. Does `batch_size=64` change the number of examples in the dataset? No
2. Does a dataloader permanently copy the whole dataset into batches? ??
3. When is the transform applied: at dataset construction or when an example is retrieved? dataset construction
4. Why can the final batch be smaller than the configured batch size? remainder, e.g. 1000%64=16

## Part 2 — Extend the configuration

Add these data settings to `ExperimentConfig`:

```python
data_path: Path = Path("data")
num_workers: int = 0
```

Validate that `num_workers` is not negative.

Keep `num_workers=0` for this Windows environment while learning the pipeline. A later lesson will benchmark workers rather than assuming that a larger value is faster.

Do not add train/test dataset sizes to configuration; those are properties of FashionMNIST, not experiment choices.

## Part 3 — Create `data.py`

Create a new module named `data.py`. Use small functions with explicit responsibilities rather than one function that performs every possible data operation.

Use these interfaces as the design target:

```python
def create_fashion_mnist_transform():
    """Return the shared image-to-float-tensor transform."""


def create_fashion_mnist_dataset(data_path, *, train, download=True):
    """Return the requested FashionMNIST dataset split."""


def create_dataloader(dataset, *, batch_size, shuffle, num_workers=0):
    """Return a dataloader with explicit sampling behaviour."""
```

The shared transform must preserve the current behaviour:

```python
v2.Compose([
    v2.ToImage(),
    v2.ToDtype(torch.float32, scale=True),
])
```

Design requirements:

- `create_fashion_mnist_dataset` must use the shared transform function.
- `train` must be a required keyword argument so a caller cannot accidentally select the wrong split positionally.
- `create_dataloader` must receive `shuffle` explicitly.
- Do not use global datasets or dataloaders inside `data.py`.
- Do not download or construct data merely by importing `data.py`.

## Part 4 — Refactor the callers

Update `training.py` so it uses the new module to create:

```text
training dataset: train=True
training loader:  shuffle=True

test dataset:     train=False
test loader:      shuffle=False
```

Update `main.py` so it constructs only the test dataset and test loader. It should not construct training data merely to evaluate a checkpoint.

After the refactor, `main.py` and `training.py` should no longer import these directly:

```python
from torchvision import datasets
from torchvision.transforms import v2
```

They should obtain data through `data.py` instead.

Also carry forward the remaining checkpoint-loading cleanup in `main.py`:

```python
device = config.get_device()

state_dict = torch.load(
    config.checkpoint_path,
    weights_only=True,
    map_location=device,
)
```

Use that same `device` variable for model placement and evaluation.

Do not run `training.py` during this lesson.

## Part 5 — Verify the pipeline

Write a temporary check or a small reusable test that verifies:

```text
training examples = 60000
test examples = 10000
training batch images shape = [64, 1, 28, 28]
training batch targets shape = [64]
image dtype = torch.float32
target dtype = torch.int64
minimum image value >= 0
maximum image value <= 1
```

Verify the sampling strategies without guessing from observed label order:

```python
from torch.utils.data import RandomSampler, SequentialSampler

assert isinstance(train_loader.sampler, RandomSampler)
assert isinstance(test_loader.sampler, SequentialSampler)
```

Why this check is better than inspecting the first few labels: even a shuffled sequence can coincidentally resemble the original order, while the sampler type directly verifies the configured behaviour.

Finally, run `main.py`. The existing checkpoint must remain approximately:

```text
device=cpu
examples=10000
test_loss=2.160762
test_accuracy=39.31%
```

If evaluation changes, compare transforms and test-split selection before proceeding.

## Part 6 — Training, validation, and test responsibilities

Complete this table:

| Split | Updates weights? | Used to choose hyperparameters? | Used for final performance estimate? |
|---|---:|---:|---:|
| Training | yes | no | no |
| Validation | no | yes | no |
| Test | no | no | yes |

Then answer:

1. Why should augmentation normally be applied to training data but not validation or test data? Augmenting data involves using mathematical transformations (stretch, rotate, etc.), doing it for the validation cause overfitting or results that would otherwise not be repeatable with normal data
2. Why is checking test accuracy after every experimental change a form of information leakage? we might make changes which improve the current test accuracy but does not generalise.
3. If validation accuracy improves but test accuracy declines, what might that suggest? overfitting
4. Why should preprocessing that learns statistics be fitted only on training data? leakage



For now, FashionMNIST still has only its official train and test datasets in the program. A later lesson will split training data into distinct training and validation subsets. Until then, understand that repeatedly using the test set to make decisions weakens its value as a final independent estimate.

## Part 7 — Record the data contract

Add your measured values here:

```text
data_path=data
num_workers=0
train_dataset_size=60000
test_dataset_size=10000
train_sampler=RandomSampler
test_sampler=SequentialSampler
image_batch_shape=[64, 1, 28, 28]
target_batch_shape=[64]
image_dtype=torch.float32
target_dtype=torch.int64
image_value_range=[0.0, 1.0]
```

Answer in one paragraph: what assumptions does the model make about the data it receives, and where are those assumptions currently enforced?
the neural network takes in tensors of shape [28, 28] of type float32

## Optional stretch task

Add a `drop_last` keyword to `create_dataloader`, defaulting to `False`, and explain why dropping the final batch can sometimes be useful during training but is usually wrong during evaluation. Keep it `False` for both loaders in this lesson.

## Definition of done

Lesson 003 is complete when:

- `data.py` contains reusable transform, dataset, and dataloader functions.
- Importing `data.py` has no download or dataset-construction side effects.
- `main.py` and `training.py` no longer duplicate torchvision dataset/transform construction.
- Training uses a random sampler and test evaluation uses a sequential sampler.
- Dataset sizes, tensor shapes, dtypes, and value ranges are verified.
- Running `main.py` preserves the established baseline.
- `model.pth` has not been overwritten.
- The split-responsibility table, four written answers, and data contract are complete.

## Next lesson

Lesson 004 will restructure `training.py` so importing it cannot start training, remove global runtime dependencies from the training function, and introduce a clear program entry point.

