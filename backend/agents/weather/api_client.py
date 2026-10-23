import logging
import httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.db.models.env.weather_reading import WeatherReading, WeatherSource

logger = logging.getLogger(__name__)

# Default coordinates for Shivamogga/Dakshina Kannada region if unconfigured
DEFAULT_LAT = 12.9141
DEFAULT_LON = 74.8560


def get_grid_region_key(lat: float, lon: float) -> str:
    """
    Rounds latitude and longitude to 2 decimal places to create a ~1.1 km grid cell region_key.
    All farms within the same grid cell share a single weather cache.
    """
    return f"grid_{round(lat, 2):.2f}_{round(lon, 2):.2f}"


def _wmo_code_to_condition(code: int) -> str:
    if code == 0:
        return "Sunny"
    elif code in [1, 2]:
        return "Partly Cloudy"
    elif code == 3:
        return "Overcast"
    elif code in [45, 48]:
        return "Foggy"
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Rainy"
    elif code in [95, 96, 99]:
        return "Thunderstorm"
    return "Cloudy"


def fetch_live_weather(lat: float | None = None, lon: float | None = None) -> dict:
    """
    Fetches current weather conditions, 24h hourly forecast, and 7-day daily forecast
    from Open-Meteo API (no API key required).
    """
    use_default = (lat is None or lon is None)
    target_lat = DEFAULT_LAT if use_default else lat
    target_lon = DEFAULT_LON if use_default else lon

    location_source = "default_fallback" if use_default else "farm_coordinates"
    region_key = get_grid_region_key(target_lat, target_lon)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": target_lat,
        "longitude": target_lon,
        "current": "temperature_2m,relative_humidity_2m,rain",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,rain",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7,
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                current_data = data.get("current", {})

                temp = float(current_data.get("temperature_2m", 26.5))
                hum = float(current_data.get("relative_humidity_2m", 82.0))
                rain = float(current_data.get("rain", 0.0))

                # 1. Parse 24-hour hourly forecast
                hourly_raw = data.get("hourly", {})
                times = hourly_raw.get("time", [])
                h_temps = hourly_raw.get("temperature_2m", [])
                h_hums = hourly_raw.get("relative_humidity_2m", [])
                h_probs = hourly_raw.get("precipitation_probability", [])
                h_rains = hourly_raw.get("rain", [])

                hourly_forecast = []
                for i in range(min(24, len(times))):
                    t_str = times[i]
                    # Extract HH:MM
                    time_label = t_str.split("T")[1][:5] if "T" in t_str else t_str[-5:]
                    hourly_forecast.append({
                        "time": time_label,
                        "temperature": float(h_temps[i]) if i < len(h_temps) else temp,
                        "humidity": float(h_hums[i]) if i < len(h_hums) else hum,
                        "precipitation_probability": float(h_probs[i]) if i < len(h_probs) else 0.0,
                        "rain_mm": float(h_rains[i]) if i < len(h_rains) else 0.0,
                    })

                # 2. Parse 7-day daily forecast
                daily_raw = data.get("daily", {})
                d_dates = daily_raw.get("time", [])
                d_maxs = daily_raw.get("temperature_2m_max", [])
                d_mins = daily_raw.get("temperature_2m_min", [])
                d_sums = daily_raw.get("precipitation_sum", [])
                d_prob_maxs = daily_raw.get("precipitation_probability_max", [])
                d_codes = daily_raw.get("weather_code", [])

                weekly_forecast = []
                for i in range(min(7, len(d_dates))):
                    date_str = d_dates[i]
                    try:
                        d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        day_label = d_obj.strftime("%a")
                    except Exception:
                        day_label = f"Day {i+1}"

                    t_max = float(d_maxs[i]) if i < len(d_maxs) else temp + 2.0
                    t_min = float(d_mins[i]) if i < len(d_mins) else temp - 4.0
                    p_sum = float(d_sums[i]) if i < len(d_sums) else 0.0
                    p_prob = float(d_prob_maxs[i]) if i < len(d_prob_maxs) else 0.0
                    w_code = int(d_codes[i]) if i < len(d_codes) else 0

                    # Compute estimated disease risk for day
                    day_hum_est = 90.0 if p_sum > 5.0 or p_prob > 60 else (75.0 if p_prob > 30 else 60.0)
                    day_risk = round(min(100.0, (day_hum_est * 0.45) + (p_sum * 2.5) + (15.0 if 20 <= t_min <= 28 else 5.0)), 1)
                    if day_risk >= 75.0:
                        risk_lvl = "urgent"
                    elif day_risk >= 55.0:
                        risk_lvl = "high"
                    elif day_risk >= 35.0:
                        risk_lvl = "medium"
                    else:
                        risk_lvl = "low"

                    weekly_forecast.append({
                        "date": date_str,
                        "day_name": day_label,
                        "temp_max": t_max,
                        "temp_min": t_min,
                        "precipitation_sum_mm": p_sum,
                        "precipitation_probability_max": p_prob,
                        "disease_risk_score": day_risk,
                        "disease_risk_level": risk_lvl,
                        "weather_condition": _wmo_code_to_condition(w_code),
                    })

                return {
                    "temperature": temp,
                    "humidity": hum,
                    "rainfall_mm": rain,
                    "region_key": region_key,
                    "location_source": location_source,
                    "lat": target_lat,
                    "lon": target_lon,
                    "weather_source": WeatherSource.API,
                    "is_synthetic": False,
                    "hourly_forecast": hourly_forecast,
                    "weekly_forecast": weekly_forecast,
                }
            else:
                logger.warning(f"Open-Meteo API returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.warning(f"Open-Meteo API connection error: {e}")

    # Explicit synthetic fallback when Open-Meteo API is unreachable
    logger.warning("Open-Meteo API unreachable. Using explicit synthetic_fallback data.")
    today_dt = datetime.now()
    fb_hourly = []
    for h in range(24):
        fb_hourly.append({
            "time": f"{h:02d}:00",
            "temperature": round(22.0 + (5.0 * (1 - abs(h - 14) / 12)), 1),
            "humidity": round(85.0 - (15.0 * (1 - abs(h - 14) / 12)), 1),
            "precipitation_probability": 35.0 if 12 <= h <= 18 else 10.0,
            "rain_mm": 2.5 if 14 <= h <= 16 else 0.0,
        })

    fb_weekly = []
    for d in range(7):
        cur_d = today_dt + timedelta(days=d)
        fb_weekly.append({
            "date": cur_d.strftime("%Y-%m-%d"),
            "day_name": cur_d.strftime("%a"),
            "temp_max": 28.5,
            "temp_min": 21.0,
            "precipitation_sum_mm": 8.5 if d in [1, 2, 4] else 1.0,
            "precipitation_probability_max": 70.0 if d in [1, 2, 4] else 25.0,
            "disease_risk_score": 68.0 if d in [1, 2, 4] else 42.0,
            "disease_risk_level": "high" if d in [1, 2, 4] else "medium",
            "weather_condition": "Rainy" if d in [1, 2, 4] else "Partly Cloudy",
        })

    return {
        "temperature": 26.5,
        "humidity": 88.0,
        "rainfall_mm": 12.5,
        "region_key": region_key,
        "location_source": location_source,
        "lat": target_lat,
        "lon": target_lon,
        "weather_source": WeatherSource.SYNTHETIC_FALLBACK,
        "is_synthetic": True,
        "hourly_forecast": fb_hourly,
        "weekly_forecast": fb_weekly,
    }


def backfill_historical_weather(
    db: Session,
    farm_id: str | None,
    region_key: str,
    lat: float | None = None,
    lon: float | None = None,
    days: int = 14,
) -> int:
    """
    Backfills past 14 days of real historical weather from Open-Meteo Historical Archive API
    at 6-hour sample intervals (56 readings) with source=WeatherSource.HISTORICAL_BACKFILL.
    Ensures ARIMA time-series models have sufficient historical data (>= 14 readings) immediately on farm creation.
    """
    target_lat = DEFAULT_LAT if lat is None else lat
    target_lon = DEFAULT_LON if lon is None else lon

    end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": target_lat,
        "longitude": target_lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,rain",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                logger.warning(f"Open-Meteo Historical Archive returned status {resp.status_code}")
                return 0

            data = resp.json()
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            hums = hourly.get("relative_humidity_2m", [])
            rains = hourly.get("rain", [])

            readings_to_add = []
            # Sample every 6 hours (6-hourly intervals)
            for idx in range(0, len(times), 6):
                dt_str = times[idx]
                dt = datetime.fromisoformat(dt_str).replace(tzinfo=timezone.utc)
                temp = float(temps[idx]) if temps[idx] is not None else 25.0
                hum = float(hums[idx]) if hums[idx] is not None else 80.0
                rain = float(rains[idx]) if rains[idx] is not None else 0.0

                readings_to_add.append(
                    WeatherReading(
                        farm_id=farm_id,
                        region_key=region_key,
                        temperature=temp,
                        humidity=hum,
                        rainfall_mm=rain,
                        source=WeatherSource.HISTORICAL_BACKFILL,
                        recorded_at=dt,
                    )
                )

            if readings_to_add:
                db.add_all(readings_to_add)
                db.commit()
                logger.info(f"Backfilled {len(readings_to_add)} historical readings for region {region_key}")
                return len(readings_to_add)

    except Exception as e:
        logger.warning(f"Failed to backfill historical weather from Open-Meteo: {e}")

    return 0
