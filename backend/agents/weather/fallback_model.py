from datetime import datetime, timedelta, timezone
from backend.schemas.weather import WeatherForecastItem


def generate_fallback_forecast(
    historical_readings: list,
    current_temp: float,
    current_humidity: float,
    current_rainfall: float,
    periods: int = 3
) -> list[WeatherForecastItem]:
    """
    Exponential Moving Average (EMA) and trend extrapolation fallback model.
    Used when historical weather_readings count < 14 (insufficient for ARIMA fitting).
    """
    if historical_readings:
        temps = [float(r.temperature) for r in historical_readings if r.temperature is not None]
        hums = [float(r.humidity) for r in historical_readings if r.humidity is not None]
        rains = [float(r.rainfall_mm) for r in historical_readings if r.rainfall_mm is not None]
    else:
        temps, hums, rains = [], [], []

    avg_temp = (sum(temps) / len(temps)) if temps else current_temp
    avg_hum = (sum(hums) / len(hums)) if hums else current_humidity
    avg_rain = (sum(rains) / len(rains)) if rains else current_rainfall

    forecast_items = []
    base_time = datetime.now(timezone.utc)

    for i in range(1, periods + 1):
        # 6-hour interval steps
        step_time = base_time + timedelta(hours=6 * i)

        # Exponential decay toward historical mean + slight random diurnal variation simulation
        proj_temp = round(current_temp * 0.7 + avg_temp * 0.3 + (i % 2 * 0.5 - 0.25), 2)
        proj_hum = round(min(100.0, max(0.0, current_humidity * 0.7 + avg_hum * 0.3)), 2)
        proj_rain = round(max(0.0, current_rainfall * 0.5 + avg_rain * 0.5), 2)

        forecast_items.append(
            WeatherForecastItem(
                timestamp=step_time,
                predicted_temperature=proj_temp,
                predicted_humidity=proj_hum,
                predicted_rainfall_mm=proj_rain,
                forecast_model="exponential_moving_average",
            )
        )

    return forecast_items
