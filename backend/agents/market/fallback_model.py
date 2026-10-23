import logging
from datetime import date, timedelta
import numpy as np

logger = logging.getLogger(__name__)


def generate_fallback_price_forecast(
    historical_prices: list[float],
    current_price: float | None = None,
    start_date: date | None = None,
    periods: int = 7,
) -> list[dict]:
    """
    Fallback Price Forecasting Model for Arecanut when historical data is below LSTM threshold (< 67 days).
    Uses robust Linear Trend Regression & Exponential Moving Average extrapolation.
    Returns 7-day forecast items with forecast_model='linear_trend_regression'.
    """
    base_date = start_date or date.today()

    if not historical_prices:
        base_p = current_price if current_price is not None else 475.0
        historical_prices = [base_p]

    series = np.array(historical_prices, dtype=np.float64)
    n = len(series)

    # If we have at least 2 points, estimate linear slope (trend)
    if n >= 2:
        x = np.arange(n)
        slope, intercept = np.polyfit(x, series, deg=1)
        # Bounded slope to avoid unrealistic runaways on small noise
        slope = max(-5.0, min(5.0, float(slope)))
        last_fitted = intercept + (slope * (n - 1))
        # Residual standard error for confidence intervals
        residuals = series - (intercept + (slope * x))
        std_err = float(np.std(residuals)) if len(residuals) > 1 else 8.0
        std_err = max(3.0, std_err)
    else:
        slope = 0.5  # Modest upward inflation baseline
        last_fitted = float(series[-1])
        std_err = 10.0

    forecast_items = []
    for h in range(1, periods + 1):
        pred_p = round(float(last_fitted + (slope * h)), 2)
        # Widen confidence band with forecast horizon sqrt(h)
        horizon_uncertainty = std_err * (1.0 + (0.15 * np.sqrt(h)))
        lower_b = round(max(0.0, pred_p - (1.96 * horizon_uncertainty)), 2)
        upper_b = round(pred_p + (1.96 * horizon_uncertainty), 2)
        f_date = base_date + timedelta(days=h)

        forecast_items.append({
            "forecast_date": f_date,
            "predicted_price_per_kg": pred_p,
            "lower_bound": lower_b,
            "upper_bound": upper_b,
            "forecast_model": "linear_trend_regression",
        })

    return forecast_items
