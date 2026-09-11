import torch
from torchvision import datasets
from torchvision.transforms import v2
from torch.utils.data import DataLoader


def create_fashion_mnist_transform():
    """Return the shared image-to-float-tensor transform."""
    return v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
    ])


def create_fashion_mnist_dataset(data_path, *, train, download=True):
    """Return the requested FashionMNIST dataset split."""
    return datasets.FashionMNIST(
        root=data_path,
        train=train,
        download=download,
        transform=create_fashion_mnist_transform(),
    )


def create_dataloader(dataset, *, batch_size, shuffle, num_workers=0):
    """Return a dataloader with explicit sampling behaviour."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
    )