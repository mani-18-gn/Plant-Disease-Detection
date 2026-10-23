# ArecaAgent — Updated Project Folder Structure (v2)

Updated to reflect the single-Postgres, multi-schema DB design (`core`, `agronomy`, `env`, `market`, `logs`) and the farmer profile / crop-block / activity-history model. Everything else from v1 (agent split, frontend, mobile, firmware) stays the same — only `backend/db/` changes meaningfully.

```
areca-agent/
│
├── README.md
├── .gitignore
├── .env.example                      # DB URL, Gemini key, weather/data.gov.in keys, budget caps
├── docker-compose.yml                # single Postgres service + backend + frontend
│
├── backend/
│   ├── requirements.txt              # pin Python 3.11/3.12
│   ├── pyproject.toml
│   ├── main.py                       # FastAPI entrypoint, mounts all agent + core routers
│   ├── config.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   │
│   │   ├── vision/                   # Vision Agent — CNN disease detection
│   │   │   ├── router.py
│   │   │   ├── model.py
│   │   │   ├── preprocess.py
│   │   │   ├── inference.py
│   │   │   ├── train.py
│   │   │   └── weights/
│   │   │
│   │   ├── diagnosis/                # Diagnosis Agent — Bayesian validation
│   │   │   ├── router.py
│   │   │   └── bayesian.py
│   │   │
│   │   ├── weather/                  # Weather Agent — ARIMA / live API
│   │   │   ├── router.py
│   │   │   ├── arima_model.py
│   │   │   ├── fallback_model.py
│   │   │   └── api_client.py
│   │   │
│   │   ├── market/                   # Market Agent — LSTM price forecasting
│   │   │   ├── router.py
│   │   │   ├── lstm_model.py
│   │   │   ├── fallback_model.py
│   │   │   ├── data_gov_client.py
│   │   │   └── train.py
│   │   │
│   │   ├── advisory/                 # Advisory Agent — Gemini integration
│   │   │   ├── router.py
│   │   │   ├── gemini_client.py
│   │   │   ├── prompts.py
│   │   │   ├── rule_based_fallback.py
│   │   │   └── cache.py              # keyed on advisories.input_snapshot
│   │   │
│   │   ├── coordinator/              # Coordinator Agent
│   │   │   ├── router.py
│   │   │   ├── orchestrator.py
│   │   │   └── weights.py            # 35/30/20/15 weighting
│   │   │
│   │   ├── learning/                 # Learning Agent — Q-learning
│   │   │   ├── router.py
│   │   │   ├── q_learning.py
│   │   │   └── feedback_store.py
│   │   │
│   │   └── notifying/                # Notifying/Monitoring Agent
│   │       ├── router.py
│   │       ├── notifications.py
│   │       └── monitoring.py
│   │
│   ├── core/                         # NEW — farmer profile, farms, crop blocks, activity logging
│   │   ├── __init__.py
│   │   ├── router.py                 # /farmer, /farms, /crop-blocks, /activities endpoints
│   │   ├── farmer_service.py         # profile CRUD
│   │   ├── farm_service.py           # farm/plot CRUD
│   │   ├── crop_block_service.py     # crop block CRUD, age calculation
│   │   └── activity_service.py       # log fertilizer/spray/planting/harvest events
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py                # single Postgres connection, schema-aware
│   │   ├── base.py                   # declarative base + schema metadata
│   │   │
│   │   ├── models/
│   │   │   ├── core/                 # schema: core
│   │   │   │   ├── user.py
│   │   │   │   ├── farmer_profile.py
│   │   │   │   ├── farm.py
│   │   │   │   ├── crop_block.py     # NEW — planting_date, variety, tree count
│   │   │   │   └── iot_device.py
│   │   │   │
│   │   │   ├── agronomy/             # schema: agronomy
│   │   │   │   ├── farm_activity.py  # NEW — fertilizer/spray/planting/harvest log
│   │   │   │   └── disease_detection.py
│   │   │   │
│   │   │   ├── env/                  # schema: env
│   │   │   │   ├── weather_reading.py
│   │   │   │   └── soil_sensor_reading.py
│   │   │   │
│   │   │   ├── market/               # schema: market
│   │   │   │   └── market_price.py
│   │   │   │
│   │   │   └── logs/                 # schema: logs
│   │   │       ├── advisory.py
│   │   │       ├── feedback.py
│   │   │       ├── notification.py
│   │   │       └── system_log.py
│   │   │
│   │   └── migrations/               # Alembic, one migration chain across all schemas
│   │       └── versions/
│   │
│   ├── auth/
│   │   ├── jwt_handler.py
│   │   └── router.py
│   │
│   ├── schemas/                      # Pydantic request/response DTOs (mirrors db/models)
│   │   ├── farmer.py
│   │   ├── farm.py
│   │   ├── crop_block.py             # NEW
│   │   ├── activity.py               # NEW
│   │   ├── disease.py
│   │   ├── weather.py
│   │   ├── market.py
│   │   └── advisory.py
│   │
│   ├── hardware/
│   │   ├── mqtt_listener.py
│   │   └── router.py                 # /sensor-data, validates against iot_devices.device_token
│   │
│   ├── tests/
│   │   ├── test_vision.py
│   │   ├── test_weather.py
│   │   ├── test_market.py
│   │   ├── test_advisory.py
│   │   ├── test_coordinator.py
│   │   ├── test_farmer_profile.py     # NEW
│   │   └── test_activity_logging.py   # NEW
│   │
│   └── scripts/
│       ├── seed_db.py                 # seed sample farmers/farms/blocks for demo
│       └── load_test.py
│
├── data/
│   ├── kaggle_arecanut/
│   ├── local_farm_images/
│   ├── market_prices/
│   └── weather_history/
│
├── frontend-web/                     # React web dashboard
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   ├── auth.js
│   │   │   ├── farmer.js             # NEW — profile, farms, crop blocks
│   │   │   ├── activity.js           # NEW — log/view fertilizer, spray, harvest events
│   │   │   ├── disease.js
│   │   │   ├── weather.js
│   │   │   ├── market.js
│   │   │   └── advisory.js
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── FarmerProfile.jsx     # NEW — land info, crop blocks, tree age/count
│   │   │   ├── ActivityLog.jsx       # NEW — timeline of planting/fertilizer/spray history
│   │   │   ├── Weather.jsx
│   │   │   ├── Market.jsx
│   │   │   ├── DiseaseDetection.jsx
│   │   │   └── Advisory.jsx
│   │   ├── components/
│   │   └── assets/
│   └── .env.example
│
├── mobile-app/
│   ├── lib/ or src/
│   │   ├── screens/
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── farmer_profile/       # NEW
│   │   │   ├── activity_log/         # NEW
│   │   │   ├── disease_detection/
│   │   │   └── alerts/
│   │   └── api/                      # mirrors frontend-web/src/api
│   └── assets/
│
├── firmware/                         # ESP32 — start parallel to Week 5-6
│   ├── platformio.ini
│   ├── src/
│   │   ├── main.cpp
│   │   ├── soil_moisture.cpp
│   │   ├── oled_display.cpp
│   │   └── wifi_mqtt_client.cpp
│   └── README.md
│
├── docs/
│   ├── phase1_report/
│   ├── phase2_report/
│   ├── db_schema.md                  # the schema doc from earlier, kept in-repo
│   ├── architecture_diagram.png
│   ├── api_reference.md
│   └── presentation/
│       ├── slides.pptx
│       └── demo_script.md
│
└── infra/
    ├── postgres_init.sql              # creates the 5 schemas: core, agronomy, env, market, logs
    └── deployment_notes.md
```

## What changed from v1

| Area | v1 | v2 |
|---|---|---|
| Databases | Assumed 5 separate physical DBs | Single Postgres, 5 logical schemas (`core`, `agronomy`, `env`, `market`, `logs`) |
| `backend/db/models/` | Flat, one file per old "DB" concept | Organized into subfolders matching the 5 schemas; adds `farmer_profile`, `farm`, `crop_block`, `farm_activity` |
| New service layer | — | `backend/core/` — dedicated to farmer profile, farms, crop blocks, and activity logging (separate from the AI agents, since this is core CRUD, not intelligence) |
| Frontend/mobile | Only Dashboard/Weather/Market/Disease/Advisory pages | Adds `FarmerProfile` (land + crop block info) and `ActivityLog` (planting/fertilizer/spray timeline) pages |
| `infra/postgres_init.sql` | Generic | Now explicitly creates the 5 schemas on first run |

## Notes on ownership (still 4-person split)
- **Person A (Vision + Diagnosis):** unchanged — `backend/agents/vision/`, `backend/agents/diagnosis/`, plus now consumes `crop_blocks` to scope detections correctly.
- **Person B (Weather + Market):** unchanged.
- **Person C (Advisory + Coordinator + Gemini):** unchanged, but advisory input JSON now also pulls from `farm_activities` (e.g. "already sprayed 3 days ago") — worth syncing with Person D on the `core` service API early.
- **Person D (Frontend + Mobile):** absorbs the new `backend/core/` endpoints — this is straightforward CRUD, good candidate to build first since every other agent depends on `crop_block_id` existing.

## Suggested build order for `core`
Since `crop_block_id` is now a foreign key nearly everywhere (activities, disease detections, advisories), get `backend/core/` and its DB models working in Week 1, before the ML agents need something to attach their outputs to.
