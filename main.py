import torch

from model import NeuralNetwork
from config import ExperimentConfig
from data import create_fashion_mnist_dataset, create_dataloader
from evaluate import evaluate

def load_checkpoint_model(config, device):
    """Load and return the configured model on device."""
    model = NeuralNetwork().to(device)
    model.load_state_dict(
        torch.load(
            config.checkpoint_path,
            weights_only=True,
            map_location=device,
        )
    )
    return model

def evaluate_checkpoint(config, dataloader):
    """Evaluate the configured checkpoint on an existing dataloader."""
    device = config.get_device()
    metrics = evaluate(
        dataloader, 
        load_checkpoint_model(config, device),
        loss_fn=config.get_loss_func(reduction="mean"),
        device=device
    )
    return metrics

def run_evaluation(config):
    """Construct the complete test-data workflow and return its metrics."""
    dataset = create_fashion_mnist_dataset(
        data_path=config.data_path,
        train=False,
        download=True
    )
    dataloader = create_dataloader(
        dataset=dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers
    )
    return evaluate_checkpoint(config, dataloader)

def main():
    """Run and report the full checkpoint evaluation."""
    metrics = run_evaluation(ExperimentConfig())
    print(f"examples={metrics['examples']}")
    print(f"eval_loss={metrics['loss']:.6f}")
    print(f"eval_accuracy={metrics['accuracy']:.2%}")

if __name__ == "__main__":
    main()