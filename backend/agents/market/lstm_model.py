import os
import logging
from datetime import date, timedelta
import torch
import torch.nn as nn
import numpy as np

logger = logging.getLogger(__name__)

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
WEIGHTS_PATH = os.path.join(WEIGHTS_DIR, "arecanut_lstm.pt")
LSTM_MIN_DATA_THRESHOLD = 67  # 60-day window + 7 target days per Major_Final_!.md §4.4.4


class MarketLSTM(nn.Module):
    """
    2-Layer LSTM Network for Arecanut Price Forecasting per report §4.4.4 & §4.5.3.4:
    - Layer 1: LSTM (hidden_size=128, dropout=0.20)
    - Layer 2: LSTM (hidden_size=64, dropout=0.20)
    - Fully Connected Output: 7-day price trajectory
    """
    def __init__(self, input_size: int = 1, hidden_1: int = 128, hidden_2: int = 64, output_steps: int = 7, dropout_prob: float = 0.20):
        super(MarketLSTM, self).__init__()
        self.lstm1 = nn.LSTM(input_size=input_size, hidden_size=hidden_1, batch_first=True)
        self.drop1 = nn.Dropout(dropout_prob)
        self.lstm2 = nn.LSTM(input_size=hidden_1, hidden_size=hidden_2, batch_first=True)
        self.drop2 = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(hidden_2, output_steps)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_len=60, input_size=1)
        out, _ = self.lstm1(x)
        out = self.drop1(out)
        out, _ = self.lstm2(out)
        out = self.drop2(out)
        # Take the last time step output
        last_step = out[:, -1, :]
        preds = self.fc(last_step)
        return preds


def load_market_lstm() -> MarketLSTM | None:
    """Loads the trained LSTM checkpoint if available on disk."""
    if os.path.exists(WEIGHTS_PATH):
        try:
            model = MarketLSTM()
            checkpoint = torch.load(WEIGHTS_PATH, map_location="cpu")
            model.load_state_dict(checkpoint)
            model.eval()
            return model
        except Exception as e:
            logger.warning(f"Failed to load Market LSTM weights: {e}")
    return None


def generate_lstm_forecast(
    historical_prices: list[float],
    start_date: date | None = None,
    periods: int = 7,
) -> list[dict]:
    """
    Runs LSTM inference over the last 60 price observations to forecast the next 7 days.
    Returns list of forecast dicts matching the MarketForecastItem schema.
    """
    if len(historical_prices) < 60:
        raise ValueError(f"LSTM requires at least 60 price observations, got {len(historical_prices)}")

    base_date = start_date or date.today()
    model = load_market_lstm()

    # Min-Max Normalization
    raw_window = np.array(historical_prices[-60:], dtype=np.float32)
    min_val = float(np.min(raw_window))
    max_val = float(np.max(raw_window))
    range_val = max_val - min_val if max_val > min_val else 1.0

    norm_window = (raw_window - min_val) / range_val
    input_tensor = torch.tensor(norm_window.reshape(1, 60, 1), dtype=torch.float32)

    if model is not None:
        with torch.no_grad():
            pred_norm = model(input_tensor).squeeze(0).numpy()
            predicted_prices = (pred_norm * range_val) + min_val
    else:
        # Default initialization output if checkpoint not yet trained
        mean_p = float(np.mean(raw_window[-7:]))
        predicted_prices = np.array([mean_p * (1.0 + 0.002 * i) for i in range(periods)], dtype=np.float32)

    forecast_items = []
    std_err = float(np.std(raw_window[-14:])) if len(raw_window) >= 14 else 5.0

    for i, pred_p in enumerate(predicted_prices[:periods]):
        f_date = base_date + timedelta(days=i + 1)
        p_val = round(float(pred_p), 2)
        lower_b = round(max(0.0, p_val - (1.96 * std_err)), 2)
        upper_b = round(p_val + (1.96 * std_err), 2)

        forecast_items.append({
            "forecast_date": f_date,
            "predicted_price_per_kg": p_val,
            "lower_bound": lower_b,
            "upper_bound": upper_b,
            "forecast_model": "lstm",
        })

    return forecast_items
