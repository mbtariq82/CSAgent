import math
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from evaluate import evaluate

model = nn.Identity()
loss_fn = nn.CrossEntropyLoss(reduction="mean")
device = torch.device("cpu")

### Aggregration test
logits = torch.tensor([
    [5.0, 0.0],  # predicts class 0: correct
    [0.0, 5.0],  # predicts class 1: correct
    [2.0, 1.0],  # predicts class 0: target will be 1
])
targets = torch.tensor([0, 1, 1])
dataset = TensorDataset(logits, targets)
dataloader = DataLoader(dataset, batch_size=2, shuffle=False)

metrics = evaluate(dataloader, model, loss_fn, device)
expected_loss = F.cross_entropy(logits, targets, reduction="mean").item()

assert metrics["examples"] == 3
assert math.isclose(metrics["loss"], expected_loss, rel_tol=1e-6)
assert math.isclose(metrics["accuracy"], 2 / 3, rel_tol=1e-6)
assert isinstance(metrics["loss"], float)
assert isinstance(metrics["accuracy"], float)
assert isinstance(metrics["examples"], int)


### Empty dataloader
empty_dataset = TensorDataset(
    torch.empty((0, 2)),
    torch.empty((0,), dtype=torch.long),
)
empty_dataloader = DataLoader(empty_dataset, batch_size=2)
try:
    evaluate(empty_dataloader, model, loss_fn, device)
except ValueError:
    pass
else:
    raise AssertionError("Empty evaluation data should raise ValueError")


### Non-finite loss
nan_dataset = TensorDataset(
    torch.tensor([[float("nan"), 0.0]]),
    torch.tensor([0]),
)
nan_dataloader = DataLoader(nan_dataset)
try:
    evaluate(nan_dataloader, model, loss_fn, device)
except RuntimeError:
    pass
else:
    raise AssertionError("Non-finite evaluation loss should raise RuntimeError")


### No gradients
linear_model = nn.Linear(2, 2)
evaluate(dataloader, linear_model, loss_fn, device)
assert all(parameter.grad is None for parameter in linear_model.parameters())
assert linear_model.training is False
