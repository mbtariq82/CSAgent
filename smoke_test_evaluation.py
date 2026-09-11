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