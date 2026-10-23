import os
import logging
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from backend.agents.market.lstm_model import MarketLSTM, WEIGHTS_DIR, WEIGHTS_PATH, LSTM_MIN_DATA_THRESHOLD

logger = logging.getLogger(__name__)


def mape_loss(y_pred: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
    """Mean Absolute Percentage Error (MAPE) loss per report §4.4.4."""
    return torch.mean(torch.abs((y_true - y_pred) / (torch.abs(y_true) + 1e-6))) * 100.0


def create_sequences(data: np.ndarray, window_size: int = 60, target_size: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """Generates sliding window sequences: 60 past days -> 7 future target days."""
    X, y = [], []
    for i in range(len(data) - window_size - target_size + 1):
        X.append(data[i : i + window_size])
        y.append(data[i + window_size : i + window_size + target_size])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train_market_lstm(
    price_series: list[float],
    epochs: int = 50,
    lr: float = 0.001,
    batch_size: int = 16,
) -> dict:
    """
    Trains the 2-layer Market LSTM model when historical observations >= 67.
    Saves the best checkpoint to weights/arecanut_lstm.pt.
    """
    if len(price_series) < LSTM_MIN_DATA_THRESHOLD:
        raise ValueError(f"Insufficient historical data ({len(price_series)} < {LSTM_MIN_DATA_THRESHOLD}) to train LSTM.")

    os.makedirs(WEIGHTS_DIR, exist_ok=True)

    data = np.array(price_series, dtype=np.float32)
    min_val, max_val = float(np.min(data)), float(np.max(data))
    range_val = max_val - min_val if max_val > min_val else 1.0
    norm_data = (data - min_val) / range_val

    X, y = create_sequences(norm_data, window_size=60, target_size=7)
    if len(X) == 0:
        raise ValueError("Could not construct training windows from historical series.")

    X_tensor = torch.tensor(X[:, :, np.newaxis], dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    model = MarketLSTM()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_loss = float("inf")
    best_weights = None

    model.train()
    for epoch in range(epochs):
        permutation = torch.randperm(X_tensor.size(0))
        epoch_losses = []

        for i in range(0, X_tensor.size(0), batch_size):
            indices = permutation[i : i + batch_size]
            batch_x, batch_y = X_tensor[indices], y_tensor[indices]

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = mape_loss(preds, batch_y)
            loss.backward()
            optimizer.step()

            epoch_losses.append(loss.item())

        avg_loss = float(np.mean(epoch_losses))
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_weights = model.state_dict()

    if best_weights is not None:
        torch.save(best_weights, WEIGHTS_PATH)
        logger.info(f"Saved Market LSTM checkpoint to {WEIGHTS_PATH} with best MAPE loss: {best_loss:.2f}%")

    return {
        "status": "trained",
        "best_mape_loss": round(best_loss, 2),
        "checkpoint_path": WEIGHTS_PATH,
    }


if __name__ == "__main__":
    # Smoke test synthetic training run
    synthetic_series = [450.0 + (i * 0.2) + (5.0 * np.sin(i / 5.0)) for i in range(100)]
    res = train_market_lstm(synthetic_series, epochs=5)
    print("Training result:", res)
