from config import ExperimentConfig
from data import (
    create_fashion_mnist_dataset,
    create_dataloader,
)


def main():
    config = ExperimentConfig()

    train_dataset = create_fashion_mnist_dataset(
        config.data_path,
        train=True,
    )
    test_dataset = create_fashion_mnist_dataset(
        config.data_path,
        train=False,
    )

    train_loader = create_dataloader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
    )
    test_loader = create_dataloader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
    )

    images, targets = next(iter(train_loader))

    print(f"data_path={config.data_path}")
    print(f"num_workers={config.num_workers}")
    print(f"train_dataset_size={len(train_dataset)}")
    print(f"test_dataset_size={len(test_dataset)}")
    print(f"train_sampler={type(train_loader.sampler).__name__}")
    print(f"test_sampler={type(test_loader.sampler).__name__}")
    print(f"image_batch_shape={list(images.shape)}")
    print(f"target_batch_shape={list(targets.shape)}")
    print(f"image_dtype={images.dtype}")
    print(f"target_dtype={targets.dtype}")
    print(
        f"observed_image_value_range="
        f"[{images.min().item()}, {images.max().item()}]"
    )


if __name__ == "__main__":
    main()