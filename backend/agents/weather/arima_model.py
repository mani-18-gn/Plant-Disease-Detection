import logging
from datetime import datetime, timedelta, timezone
from backend.schemas.weather import WeatherForecastItem
from backend.agents.weather.fallback_model import generate_fallback_forecast

logger = logging.getLogger(__name__)

# Minimum historical readings required to attempt ARIMA time-series fitting
ARIMA_MIN_READINGS = 14


def generate_weather_forecast(
    historical_readings: list,
    current_temp: float,
    current_humidity: float,
    current_rainfall: float,
    periods: int = 3
) -> list[WeatherForecastItem]:
    """
    Generate weather forecast for next 3 periods (6-hour intervals).
    1. Checks if historical_readings count >= 14 (ARIMA_MIN_READINGS).
    2. If count >= 14 and statsmodels is installed, fits ARIMA time-series model.
    3. If count < 14 or statsmodels is missing/throws error, automatically falls back to fallback_model.py.
    """
    if len(historical_readings) < ARIMA_MIN_READINGS:
        logger.info(f"Historical readings count ({len(historical_readings)}) < {ARIMA_MIN_READINGS}. Using fallback model.")
        return generate_fallback_forecast(
            historical_readings=historical_readings,
            current_temp=current_temp,
            current_humidity=current_humidity,
            current_rainfall=current_rainfall,
            periods=periods,
        )

    try:
        import statsmodels.tsa.arima.model as arima

        temps = [float(r.temperature) for r in historical_readings if r.temperature is not None]
        hums = [float(r.humidity) for r in historical_readings if r.humidity is not None]
        rains = [float(r.rainfall_mm) for r in historical_readings if r.rainfall_mm is not None]

        # Fit ARIMA(1,1,1) for temperature
        model_temp = arima.ARIMA(temps, order=(1, 1, 1)).fit()
        pred_temps = model_temp.forecast(steps=periods)

        # Fit ARIMA(1,1,1) for humidity
        model_hum = arima.ARIMA(hums, order=(1, 1, 1)).fit()
        pred_hums = model_hum.forecast(steps=periods)

        # Fit ARIMA(1,1,1) for rainfall
        model_rain = arima.ARIMA(rains, order=(1, 1, 1)).fit()
        pred_rains = model_rain.forecast(steps=periods)

        base_time = datetime.now(timezone.utc)
        forecast_items = []

        for i in range(periods):
            step_time = base_time + timedelta(hours=6 * (i + 1))
            forecast_items.append(
                WeatherForecastItem(
                    timestamp=step_time,
                    predicted_temperature=round(float(pred_temps[i]), 2),
                    predicted_humidity=round(min(100.0, max(0.0, float(pred_hums[i]))), 2),
                    predicted_rainfall_mm=round(max(0.0, float(pred_rains[i])), 2),
                    forecast_model="arima",
                )
            )

        return forecast_items

    except Exception as e:
        logger.warning(f"ARIMA fitting failed: {e}. Falling back to exponential moving average model.")
        return generate_fallback_forecast(
            historical_readings=historical_readings,
            current_temp=current_temp,
            current_humidity=current_humidity,
            current_rainfall=current_rainfall,
            periods=periods,
        )
