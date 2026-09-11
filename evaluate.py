import torch

def evaluate(dataloader, model, loss_fn, device):
    """Evaluate every example and return numeric classification metrics."""
    total_loss, correct, total_examples = 0.0, 0, 0
    model.eval()
    with torch.inference_mode():
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(device), y.to(device)
            pred = model(X)
            loss = loss_fn(pred, y)
            if not torch.isfinite(loss).item():
                raise RuntimeError(
                    f"Non-finite evaluation loss at batch {batch}: {loss.item()}"
                )
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
            batch_size = X.size(0)
            total_loss += loss.item() * batch_size
            total_examples += batch_size
        if total_examples == 0:
            raise ValueError("Cannot evaluate an empty dataloader")
    total_loss /= total_examples
    correct /= total_examples
    return {
        'examples': total_examples,
        'loss': total_loss, 
        'accuracy': correct
    }
