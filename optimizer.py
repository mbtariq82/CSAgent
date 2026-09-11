import torch


def create_optimizer(config, model):
    parameters = model.parameters()

    if config.optimizer == "sgd":
        return torch.optim.SGD(
            parameters,
            lr=config.learning_rate,
            momentum=config.momentum,
            weight_decay=config.weight_decay,
        )

    raise ValueError(
        f"Unsupported optimizer: {config.optimizer}"
    )