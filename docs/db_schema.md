# PlantGuard — Database Schema Specification

One PostgreSQL database organized into 5 logical schemas: `core`, `agronomy`, `env`, `market`, `logs`.

## Schema: `core`
- `users`: Auth credentials and roles (`farmer`, `admin`).
- `farmer_profiles`: Personal info, location (village/district/pincode), language, default mandi.
- `farms`: Geo-located land plots (lat/lon, total acreage, soil type, irrigation type).
- `crop_blocks`: Perennial planting blocks (variety, planting date, tree count, spacing).
- `iot_devices`: ESP32 device registrations & access tokens.

## Schema: `agronomy`
- `farm_activities`: Activity history (fertilizer, spray, harvest, irrigation) indexed by block, type, date.
- `disease_detections`: Vision agent CNN output + Bayesian posterior validation.

## Schema: `env`
- `weather_readings`: Temperature, humidity, rainfall (API/forecast/history).
- `soil_sensor_readings`: Moisture % telemetry from IoT devices.

## Schema: `market`
- `market_prices`: Mandi commodity prices per kg from Data.gov.in.

## Schema: `logs`
- `advisories`: Generated recommendations + Gemini input JSON snapshot.
- `feedback`: Farmer ratings (1-5) and outcome notes feeding RL Learning Agent.
- `notifications`: Multi-channel message queue (SMS, push, in-app).
- `system_logs`: Audit and error logs.
