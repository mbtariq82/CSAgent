import torch
import torch.nn as nn
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 42
    batch_size: int = 64
    epochs: int = 5
    learning_rate: float = 1e-3
    checkpoint_path: Path = Path("model.pth")
    requested_device: str = 'auto'
    loss_func: str = 'cross_entropy'
    optimizer: str = 'sgd'
    momentum: float = 0.0
    weight_decay: float = 0.0
    data_path: Path = Path("data")
    num_workers: int = 0

    def __post_init__(self):
        if self.requested_device not in ['auto', 'cpu', 'cuda']:
            raise ValueError(f"Invalid requested_device: {self.requested_device}. Must be 'auto', 'cpu', or 'cuda'.")
        if self.batch_size <= 0:
            raise ValueError(f"Invalid batch_size: {self.batch_size}. Must be a positive integer.")
        if self.epochs <= 0:
            raise ValueError(f"Invalid epochs: {self.epochs}. Must be a positive integer.")
        if self.learning_rate <= 0:
            raise ValueError(f"Invalid learning_rate: {self.learning_rate}. Must be a positive float.")
        if self.num_workers < 0:
            raise ValueError(f"Invalid num_workers: {self.num_workers}. Must be a non-negative integer.")

    def get_device(self):
        if self.requested_device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            else:
                return torch.device("cpu")
        return torch.device(self.requested_device)

    def get_loss_func(self, reduction="mean"):
        if self.loss_func == 'cross_entropy':
            return nn.CrossEntropyLoss(reduction=reduction)
        raise ValueError(f"Unsupported loss function: {self.loss_func}")
