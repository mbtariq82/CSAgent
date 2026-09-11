import torch

from data import create_fashion_mnist_dataset, create_dataloader
from model import NeuralNetwork
from config import ExperimentConfig
from optimizer import create_optimizer


def train_one_epoch(dataloader, model, loss_fn, optimizer, device):
    model.train()
    total_loss, total_examples = 0.0, 0
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        optimizer.zero_grad()
        pred = model(X)
        loss = loss_fn(pred, y)
        if not torch.isfinite(loss).item():
            raise RuntimeError(
                f"Non-finite training loss at batch {batch}: {loss.item()}"
            )
        loss.backward()
        optimizer.step()
        batch_size = X.size(0)
        total_loss += loss.item() * batch_size
        total_examples += batch_size
    if total_examples == 0:
        raise ValueError("Empty dataloader")
    return {
        "examples": total_examples,
        "loss": total_loss / total_examples,
    }


def run_training(config):
    training_data = create_fashion_mnist_dataset(
        data_path=config.data_path,
        train=True,
        download=True
    )
    dataloader = create_dataloader(
        dataset=training_data,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers
    )
    device = config.get_device()
    model = NeuralNetwork().to(device)
    loss_fn = config.get_loss_func(reduction="mean")
    optimizer = create_optimizer(config, model)
    for t in range(config.epochs):
        metrics = train_one_epoch(dataloader, model, loss_fn, optimizer, device)
        print(f"epoch={t + 1}")
        print(f"examples={metrics['examples']}")
        print(f"train_loss={metrics['loss']:.6f}")
    print("training_complete=True")
    return model

def main():
    """Train, save, and report the configured model."""
    config = ExperimentConfig()
    model = run_training(config)
    torch.save(model.state_dict(), config.checkpoint_path)
    print(f"checkpoint_saved={config.checkpoint_path}")

if __name__ == "__main__":
    main()
