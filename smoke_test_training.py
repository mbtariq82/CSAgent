import math
import hashlib
from torch.utils.data import Subset

from config import ExperimentConfig
from model import NeuralNetwork
from data import create_fashion_mnist_dataset, create_dataloader
from optimizer import create_optimizer
from train import train_one_epoch


def checkpoint_signature(path):
    """Return checkpoint metadata and content hash, or None if it is absent."""
    if not path.exists():
        return None

    stat = path.stat()
    content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    return stat.st_mtime_ns, stat.st_size, content_hash

def main():
    config = ExperimentConfig()
    checkpoint_before = checkpoint_signature(config.checkpoint_path)
    device = config.get_device()
    dataset = create_fashion_mnist_dataset(
        config.data_path,
        train=True,
        download=False
    )
    small_dataset = Subset(dataset, range(128))
    model = NeuralNetwork().to(device)
    before = next(model.parameters()).detach().clone()
    dataloader = create_dataloader(
        small_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers
    )
    metrics = train_one_epoch(
        dataloader, 
        model, 
        config.get_loss_func(reduction="mean"), 
        create_optimizer(config, model), 
        device
    )
    after = next(model.parameters()).detach()
    parameter_delta = (after - before).abs().sum().item()
    assert metrics["examples"] == 128
    assert math.isfinite(metrics["loss"])
    assert metrics["loss"] > 0
    assert parameter_delta > 0
    checkpoint_after = checkpoint_signature(config.checkpoint_path)
    assert checkpoint_after == checkpoint_before, "Smoke test changed the checkpoint"
    assert set(metrics) == {"loss", "examples"}

if __name__=='__main__':
    main()