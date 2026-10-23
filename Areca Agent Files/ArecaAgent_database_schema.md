# ArecaAgent — Database Schema (Farmer Profile + Activity History)

**Recommendation:** One PostgreSQL database, organized into logical schemas (`core`, `agronomy`, `market`, `env`, `logs`) instead of 5 physically separate databases. This preserves the conceptual separation from your report while keeping foreign keys intact across farmer → farm → crop block → activity/disease/advisory.

---

## `core` schema — Users & Farmer Profile

### `users`
Auth table. One row per login credential.
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| username | text unique | |
| phone | text unique | used for SMS alerts too |
| password_hash | text | |
| role | enum(farmer, admin) | |
| created_at | timestamptz | |
| last_login_at | timestamptz | |

### `farmer_profiles`
1:1 with `users`. This is the "who is this farmer" data.
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK → users.id | |
| full_name | text | |
| village / taluk / district / state | text | for weather + market region matching |
| pincode | text | |
| preferred_language | text | for advisory text localization |
| preferred_mandi | text | default market for price comparisons |
| created_at | timestamptz | |

### `farms`
A farmer can own/operate more than one plot of land — model this as 1:N from day one, even if most farmers only add one.
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| farmer_id | UUID FK → farmer_profiles.id | |
| farm_name | text | e.g. "Home garden", "North plot" |
| latitude / longitude | numeric | drives which weather-grid cell this farm uses |
| total_area_acres | numeric | |
| soil_type | text | |
| irrigation_type | enum(drip, flood, sprinkler, rainfed) | |
| created_at | timestamptz | |

### `crop_blocks`
This is the key table you were missing. Arecanut is perennial and farmers plant in batches over years — a single "farm" isn't one uniform crop. Model each planting batch as its own block so age, variety, and tree count are tracked per-block, not per-farm.
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| farm_id | UUID FK → farms.id | |
| block_name | text | e.g. "Block A – 2018 planting" |
| variety | text | e.g. Mangala, Sumangala, South Kanara |
| planting_date | date | **age is derived** = now() − planting_date, don't store age directly |
| number_of_trees | integer | |
| spacing_meters | numeric | affects disease spread modeling later |
| status | enum(active, removed, replanted) | |
| notes | text | |

### `iot_devices`
ESP32 registration, one device per farm (or per block if you scale further).
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| farm_id | UUID FK → farms.id | |
| device_token | text unique | used for MQTT/HTTP auth from firmware |
| device_type | text | e.g. "soil_moisture_v1" |
| last_seen_at | timestamptz | |

---

## `agronomy` schema — Activity History & Disease Detection

### `farm_activities`
**This is the core of "when fertilizer was put, when spraying was done."** One table, typed by `activity_type`, with a flexible JSONB `details` column so you don't need a new table for every activity type — but the fields that matter for agent reasoning (product, quantity, next-due date) are still first-class columns so agents can query them directly without parsing JSON.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| crop_block_id | UUID FK → crop_blocks.id | |
| activity_type | enum(planting, fertilizer, spraying, irrigation, pruning, weeding, harvesting, soil_test, other) | |
| activity_date | date | |
| product_used | text nullable | fertilizer/pesticide brand or compound name |
| quantity | numeric nullable | |
| quantity_unit | text nullable | kg, litre, etc. |
| cost | numeric nullable | |
| performed_by | text nullable | self / hired labor |
| details | jsonb | anything activity-specific (e.g. spray target disease, fertilizer NPK ratio) |
| logged_via | enum(app, sms, auto) | did farmer log manually or did system infer it |
| created_at | timestamptz | |

**Why this matters for your agents:** the Diagnosis Agent's Bayesian model and the Advisory Agent's rules both need "was this block sprayed in the last N days" and "when was the last fertilizer application" as direct inputs — that's why `product_used`, `activity_date`, and `activity_type` are indexed columns, not buried in JSON.

### `disease_detections`
Output of Vision + Diagnosis agents, linked to a specific crop block (not just the farm) so history stays precise.
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| crop_block_id | UUID FK → crop_blocks.id | |
| image_path | text | |
| predicted_disease | text | |
| cnn_confidence | numeric | Vision Agent output |
| posterior_probability | numeric nullable | Diagnosis Agent (Bayesian) output |
| validated | boolean | posterior > 0.75 threshold from your report |
| detected_at | timestamptz | |

---

## `env` schema — Weather & Soil Sensor Data

### `weather_readings`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| farm_id | UUID FK → farms.id | or region_key if you cache by grid cell instead of per-farm |
| temperature, humidity, rainfall_mm | numeric | |
| source | enum(api, forecast) | |
| recorded_at | timestamptz | |

### `soil_sensor_readings`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| device_id | UUID FK → iot_devices.id | |
| moisture_pct | numeric | |
| recorded_at | timestamptz | |

---

## `market` schema

### `market_prices`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| mandi_name | text | |
| commodity | text | "arecanut" + variety if data.gov.in provides it |
| price_per_kg | numeric | |
| price_date | date | |
| source | text | data.gov.in |

---

## `logs` schema — Advisory, Feedback, Notifications, System

### `advisories`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| farmer_id | UUID FK → farmer_profiles.id | |
| crop_block_id | UUID FK → crop_blocks.id nullable | some advisories are farm-level, not block-level |
| priority | enum(urgent, high, medium, low) | matches your priority matrix |
| message | text | Gemini-generated or rule-based fallback text |
| generated_by | enum(gemini, rule_fallback) | |
| input_snapshot | jsonb | the structured JSON that went into Gemini — useful for debugging/caching |
| read_status | boolean | |
| created_at | timestamptz | |

### `feedback`
Feeds the Learning Agent's Q-updates.
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| advisory_id | UUID FK → advisories.id | |
| farmer_id | UUID FK → farmer_profiles.id | |
| rating | integer (1–5) | |
| outcome_notes | text nullable | |
| created_at | timestamptz | |

### `notifications`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| farmer_id | UUID FK → farmer_profiles.id | |
| channel | enum(sms, push, in_app) | |
| content | text | |
| status | enum(sent, failed, pending) | |
| sent_at | timestamptz | |

### `system_logs`
| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| service | text | which agent/endpoint |
| level | enum(info, warning, error) | |
| message | text | |
| logged_at | timestamptz | |

---

## Relationship summary

```
users (1) ──── (1) farmer_profiles
farmer_profiles (1) ──── (N) farms
farms (1) ──── (N) crop_blocks
farms (1) ──── (N) iot_devices
crop_blocks (1) ──── (N) farm_activities      ← planting/fertilizer/spray/harvest history
crop_blocks (1) ──── (N) disease_detections
iot_devices (1) ──── (N) soil_sensor_readings
farms (1) ──── (N) weather_readings
farmer_profiles (1) ──── (N) advisories
advisories (1) ──── (N) feedback
farmer_profiles (1) ──── (N) notifications
```

## Key design decisions worth flagging to your guide

1. **Age is derived, not stored** — `crop_blocks.planting_date` lets you compute tree age at query time (`age = now() - planting_date`), so it's always accurate rather than needing periodic updates.
2. **Activity is block-level, not farm-level** — a farm can have a 2015 block and a 2022 block with very different disease risk and fertilizer schedules; logging activity against the block (not the whole farm) keeps advisories accurate.
3. **One `farm_activities` table, not one-per-type** — with a 3-month timeline, seven separate activity tables (planting_log, fertilizer_log, spray_log...) is unnecessary schema overhead. The typed + JSONB approach gives you flexibility now and you can split tables later only if a specific activity type needs heavy structured querying.
4. **`input_snapshot` on advisories** — storing exactly what was sent to Gemini for each advisory makes debugging bad advice and building your Learning Agent's training signal much easier, and doubles as your caching key (Week 6 guardrail from the roadmap).

## Suggested next step
Want me to turn this into actual SQLAlchemy models / Alembic migration files under `backend/db/models/` so you can drop it straight into the folder structure from before?
