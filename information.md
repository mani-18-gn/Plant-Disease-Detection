# BharatCrop AI / Areca-Agent — Complete System Architecture & Information Reference

> **Comprehensive Technical Blueprint & Implementation Guide**  
> System: Multi-Agent Precision Agriculture & Google-Powered Plant Pathology Platform  
> Repository: `https://github.com/mani-18-gn/Plant-Disease-Detection.git`  
> Generated: October 2026

---

## Table of Contents
1. [Executive Summary & Core Objectives](#1-executive-summary--core-objectives)
2. [Complete Technology Stack](#2-complete-technology-stack)
3. [Master Repository Directory Structure & File Map](#3-master-repository-directory-structure--file-map)
4. [Multi-Agent System Architecture (The 8 Autonomous Agents)](#4-multi-agent-system-architecture-the-8-autonomous-agents)
   - [4.1 Vision Agent (Edge Deep Learning)](#41-vision-agent-edge-deep-learning)
   - [4.2 Diagnosis Agent (Google AI Multimodal + Bayesian Belief Network)](#42-diagnosis-agent-google-ai-multimodal--bayesian-belief-network)
   - [4.3 Advisory Agent (Agronomic Guidance & LLM Cache)](#43-advisory-agent-agronomic-guidance--llm-cache)
   - [4.4 Coordinator Agent (Priority Decision Engine)](#44-coordinator-agent-priority-decision-engine)
   - [4.5 Weather Agent (Microclimate & Disease Risk)](#45-weather-agent-microclimate--disease-risk)
   - [4.6 Market Agent (LSTM Mandi Price Forecasting)](#46-market-agent-lstm-mandi-price-forecasting)
   - [4.7 Learning Agent (Q-Learning Feedback Optimization)](#47-learning-agent-q-learning-feedback-optimization)
   - [4.8 Notifying Agent (Threshold Monitoring & Alerts)](#48-notifying-agent-threshold-monitoring--alerts)
5. [AI, Deep Learning & Statistical Models](#5-ai-deep-learning--statistical-models)
6. [Database Schema & Entity Relationship Model](#6-database-schema--entity-relationship-model)
7. [Frontend Web Architecture (React 18 + Vite)](#7-frontend-web-architecture-react-18--vite)
8. [IoT Firmware & Hardware Telemetry (ESP32)](#8-iot-firmware--hardware-telemetry-esp32)
9. [REST API Endpoints & Routing Guide](#9-rest-api-endpoints--routing-guide)
10. [Configuration & Environment Variables](#10-configuration--environment-variables)
11. [Execution, Testing & Deployment](#11-execution-testing--deployment)

---

## 1. Executive Summary & Core Objectives

**BharatCrop AI (Areca-Agent)** is an enterprise-grade precision agriculture and automated crop disease identification platform. Originally built around arecanut plantation management, the system has evolved into a comprehensive, multi-crop plant pathology platform that combines **Local Edge Deep Learning (MobileNetV2 / PyTorch)** with **Google's Advanced Multimodal Generative AI (`gemini-3.1-flash-lite-preview` / `gemini-3-flash-preview`)**.

### Key System Capabilities:
- **Dual-Engine Plant Pathology**: Cross-validates local CNN image classification with cloud-based Google Gemini multimodal reasoning to eliminate false positives and generic predictions.
- **Differential Diagnosis**: Provides a primary disease diagnosis alongside at least two plausible differential alternatives, visual symptom breakdowns, and confidence assessments.
- **3-Pillar Integrated Pest Management (IPM)**: Generates actionable, grounded treatment protocols covering:
  1. *Organic / Biological Controls* (Trichoderma, Pseudomonas, neem formulations)
  2. *Chemical Controls* (Systemic fungicides, active ingredients, dosage, pre-harvest intervals)
  3. *Agronomic / Cultural Practices* (Sanitation, spacing, canopy pruning, drainage)
- **Closed-Loop Multi-Agent Collaboration**: 8 specialized agents work asynchronously to assess visual health, microclimate disease risks, mandi commodity price trends, and farmer feedback.
- **Enterprise-Ready Database Architecture**: 5-schema design (`core`, `agronomy`, `env`, `market`, `logs`) supporting SQLite for rapid local prototyping and PostgreSQL for production deployments.

---

## 2. Complete Technology Stack

| Layer | Technology | Version | Purpose & Implementation Details |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | `0.110.0` | High-performance asynchronous REST API, route declaration, dependency injection, and automatic OpenAPI documentation. |
| **ASGI Server** | Uvicorn (standard) | `0.28.0` | Fast ASGI web server supporting hot-reloading and asynchronous worker event loops. |
| **Language Runtime** | Python | `3.11+` | Primary programming language for backend agents, data science pipelines, and database ORM. |
| **Cloud Multimodal AI** | Google Gen AI SDK (`google-genai`) | `>=2.0.0` (v2.33.0) | Official Google SDK for Gemini multimodal vision analysis, differential diagnosis, and search grounding. |
| **Deep Learning (Vision)** | PyTorch & Torchvision | `2.14.0+cpu` / `0.29.1+cpu` | Inference engine for custom CNN models (`arecanut_cnn.pt`) and tensor operations. Supports CUDA (`cu121`) for GPU acceleration. |
| **Hugging Face / Transformers** | Transformers & Safetensors | `>=4.40.0` / `>=0.4.0` | Loads pre-trained MobileNetV2 38-class weights in zero-copy Safetensors format (`model.safetensors`). |
| **Data Validation & Schemas** | Pydantic & Pydantic Settings | `2.6.4` / `2.2.1` | Request/response data validation, strict schema serialization, and type-safe environment configuration loading. |
| **Database ORM** | SQLAlchemy | `2.0.28` | Modern declarative ORM supporting typed queries, session management, and relational mapping. |
| **Database Migrations** | Alembic | `1.13.1` | Schema versioning and automated DDL migrations across environments. |
| **Database Engines** | SQLite / PostgreSQL | `3.x` / `16-alpine` | Dual-engine: SQLite (`areca_agent.db`) for instant zero-dependency local execution; PostgreSQL 16 for production multi-tenant workloads. |
| **Database Drivers** | `sqlite3` / `psycopg2-binary` | `2.9.9` | Low-level C-based database connection adapters for SQLAlchemy. |
| **Authentication & Security** | PyJWT, Passlib, Bcrypt | `2.8.0`, `1.7.4`, `4.0.1` | Stateless JWT access tokens (HS256) and salted bcrypt password hashing. |
| **HTTP Client** | HTTPX | `0.27.0` | Async and sync HTTP requests for external weather APIs and Open Government Data ingestion. |
| **Data Science & ML** | NumPy, Pandas, Scikit-learn | `1.26.4`, `2.2.1`, `1.4.1` | Tabular data manipulation, time-series feature engineering, ARIMA modeling, and similarity scoring. |
| **Image Processing** | Pillow (PIL) | `>=10.0.0` | Image format conversion, dimension validation, EXIF normalization, and decodability checks. |
| **Testing Framework** | Pytest | `7.x+` | Automated unit, regression, and end-to-end integration test runner (82/82 passing tests). |
| **Frontend Framework** | React | `18.3.1` | Component-driven UI library with hooks, context, and state management. |
| **Build Tool & Dev Server** | Vite | `6.1.0` | Ultra-fast ESM frontend bundler and development server with Hot Module Replacement (HMR). |
| **Frontend Routing** | React Router DOM | `6.29.0` | Client-side routing, protected auth routes, and browser history management. |
| **Styling & Design System** | Vanilla CSS + Tailwind utilities | Custom / `tailwind-merge` | Premium dark-mode glassmorphic interface, responsive grids, and CSS variables. |
| **Iconography** | Lucide React & Hugeicons | `0.475.0` / `1.1.10` | Modern SVG iconography for agricultural metrics, alerts, navigation, and indicators. |
| **HTTP Client (Frontend)**| Axios | `1.7.9` | Promise-based HTTP client with auth token interceptors and upload progress tracking. |
| **Microcontroller / IoT** | ESP32 | ESP-WROOM-32 | Edge hardware node capturing soil moisture, temperature, and relative humidity. |
| **Embedded Framework** | PlatformIO / Arduino C++ | Latest | C++ embedded firmware development environment for ESP32. |
| **IoT Protocol** | MQTT | v3.1.1 | Lightweight publish/subscribe telemetry transport for farm sensor readings. |
| **Containerization** | Docker & Docker Compose | Compose `3.8` | Multi-container orchestration for PostgreSQL and FastAPI backend. |

---

## 3. Master Repository Directory Structure & File Map

Below is the complete file and folder breakdown of the repository:

```
Areca-Agent-main/
│
├── .env.example                                  # Master environment variable template with documentation
├── .gitignore                                    # Excludes .env, weights, databases, logs, and build artifacts
├── .pytest_cache/                                # Pytest runner cache
├── .vscode/                                      # VS Code workspace settings and launcher configs
├── alembic.ini                                   # Alembic database migration configuration
├── areca_agent.db                                # Active local SQLite database instance
├── docker-compose.yml                            # Production Docker stack (PostgreSQL + FastAPI backend)
├── information.md                                # THIS FILE: Complete system architecture and stack documentation
├── LICENSE                                       # Project open-source license (MIT)
├── pytest.ini                                    # Pytest test discovery and warning filters
├── pyrightconfig.json                            # Python language server and type checking settings
├── README.md                                     # High-level developer setup guide
├── run_backend.bat                               # Windows one-click launcher for FastAPI backend (Port 8000)
├── run_frontend.bat                              # Windows one-click launcher for Vite frontend (Port 5173)
├── test_verify_plantdoc_e2e.py                   # Automated end-to-end testing script for PlantDoc datasets
│
├── Areca Agent Files/                            # Architectural design documents & project roadmaps
│   ├── ArecaAgent_3Month_Roadmap.md              # 90-day phase-wise milestone and delivery plan
│   ├── ArecaAgent_database_schema.md             # Detailed PostgreSQL 5-schema data dictionary
│   ├── ArecaAgent_folder_structure_v2.md         # Monorepo folder organization specification
│   └── Major_Final_!.md                          # Comprehensive project thesis and academic submission
│
├── backend/                                      # CORE BACKEND SERVICE (FastAPI & Autonomous Agents)
│   ├── .env                                      # Local environment secrets (GOOGLE_API_KEY, JWT secret)
│   ├── config.py                                 # Pydantic BaseSettings loading configuration and paths
│   ├── Dockerfile                                # Container build recipe for Python FastAPI backend
│   ├── main.py                                   # FastAPI application entrypoint, router mounts & lifecycle
│   ├── pyproject.toml                            # Python package build specifications
│   ├── requirements.txt                          # Pinned Python package dependencies
│   │
│   ├── agents/                                   # THE 8 AUTONOMOUS INTELLIGENT AGENTS
│   │   ├── __init__.py                           # Module marker
│   │   │
│   │   ├── advisory/                             # 1. ADVISORY AGENT (Treatment & Agronomy)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── cache.py                          # SHA256 hashed advisory cache to prevent redundant LLM calls
│   │   │   ├── gemini_client.py                  # Gemini LLM client for agronomic recommendations
│   │   │   ├── prompts.py                        # Engineered prompt templates for agricultural expert reasoning
│   │   │   ├── router.py                         # REST endpoints for advisory generation and retrieval
│   │   │   └── rule_based_fallback.py            # Offline rule-based advisory engine when LLM is unavailable
│   │   │
│   │   ├── coordinator/                          # 2. COORDINATOR AGENT (System Orchestration)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── orchestrator.py                   # Central brain synthesizing inputs from all agents
│   │   │   ├── router.py                         # REST endpoint: POST /api/v1/coordinator/orchestrate
│   │   │   └── weights.py                        # Multi-criteria weighting matrix (35% Vision, 30% Weather, etc.)
│   │   │
│   │   ├── diagnosis/                            # 3. DIAGNOSIS AGENT (Plant Disease Pathology)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── bayesian.py                       # Bayesian Belief Network fusing vision, weather & crop stage
│   │   │   ├── google_ai.py                      # GOOGLE GEMINI MULTIMODAL PATHOLOGY ENGINE (v2.33.0)
│   │   │   └── router.py                         # Endpoints: /api/diagnose, /api/v1/diagnose, /api/diagnose/status
│   │   │
│   │   ├── learning/                             # 4. LEARNING AGENT (Reinforcement Learning)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── feedback_store.py                 # Persists farmer outcome reviews and success metrics
│   │   │   ├── q_learning.py                     # Q-learning algorithm updating advisory state-action values
│   │   │   └── router.py                         # Endpoints for submitting feedback and inspecting Q-tables
│   │   │
│   │   ├── market/                               # 5. MARKET AGENT (Commodity Economics)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── data_gov_client.py                # Client for Data.gov.in AGMARKNET mandi wholesale price APIs
│   │   │   ├── fallback_model.py                 # Exponential moving average price trend fallback
│   │   │   ├── lstm_model.py                     # PyTorch LSTM neural network for 7-day price forecasting
│   │   │   ├── router.py                         # Endpoints: /api/v1/market/prices, /api/v1/market/forecast
│   │   │   └── train.py                          # Training script for the market price LSTM model
│   │   │
│   │   ├── notifying/                            # 6. NOTIFYING AGENT (Alerts & Telemetry Monitoring)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── monitoring.py                     # Background worker evaluating telemetry thresholds
│   │   │   ├── notifications.py                  # In-app and push notification dispatch manager
│   │   │   └── router.py                         # Endpoints for retrieving user alerts and marking read
│   │   │
│   │   ├── vision/                               # 7. VISION AGENT (Edge Deep Learning Inference)
│   │   │   ├── __init__.py                       # Package initializer
│   │   │   ├── advisory_db.py                    # Static verified disease knowledge base & treatment protocols
│   │   │   ├── crop_validator.py                 # Pre-classification check verifying image is a valid plant leaf
│   │   │   ├── inference.py                      # Multi-crop MobileNetV2 & PyTorch inference pipeline
│   │   │   ├── keras_inference.py                # Legacy Keras/TensorFlow inference bridge
│   │   │   ├── model.py                          # PyTorch CNN model architectures
│   │   │   ├── preprocess.py                     # Image normalization, resizing, and tensor transformation
│   │   │   ├── router.py                         # Endpoints: /api/v1/vision/detect, /api/v1/vision/diagnose
│   │   │   ├── similarity.py                     # Embedding cosine similarity for visual feature matching
│   │   │   ├── train.py                          # Training pipeline for multi-crop classification
│   │   │   ├── web_research.py                   # Automated web lookup for rare plant diseases
│   │   │   └── weights/                          # Model binary checkpoints
│   │   │       ├── arecanut_cnn.pt               # Custom trained PyTorch CNN for Arecanut (10.4 MB)
│   │   │       └── multi_crop_mobilenetv2/       # 38-class MobileNetV2 Safetensors checkpoint
│   │   │           ├── config.json               # Model topology and label-to-id mapping
│   │   │           ├── model.safetensors         # Quantized model weights (9.2 MB)
│   │   │           └── preprocessor_config.json  # Normalization parameters (mean, std, size)
│   │   │
│   │   └── weather/                              # 8. WEATHER AGENT (Microclimate Risk Analysis)
│   │       ├── __init__.py                       # Package initializer
│   │       ├── api_client.py                     # OpenWeatherMap / Open-Meteo live API client
│   │       ├── arima_model.py                    # Auto-Regressive Integrated Moving Average weather model
│   │       ├── fallback_model.py                 # Historical climatological statistical fallback
│   │       ├── risk_score.py                     # Fungal/bacterial disease proliferation risk index
│   │       └── router.py                         # Endpoints: /api/v1/weather/current, /api/v1/weather/risk
│   │
│   ├── auth/                                     # USER AUTHENTICATION & SECURITY
│   │   ├── __init__.py                           # Package initializer
│   │   ├── jwt_handler.py                        # JWT token encoding, decoding, and password hashing
│   │   └── router.py                             # Endpoints: POST /api/v1/auth/register, /api/v1/auth/login
│   │
│   ├── core/                                     # FARM DOMAIN SERVICES & ENTITIES
│   │   ├── __init__.py                           # Package initializer
│   │   ├── activity_service.py                   # Business logic for logging farm activities (fertilizer, spray)
│   │   ├── crop_block_service.py                 # Management of individual plantation blocks, varieties, tree age
│   │   ├── farm_service.py                       # Farm geometry, boundary, soil characteristics, and irrigation
│   │   ├── farmer_service.py                     # Farmer identity, contact details, language preferences
│   │   └── router.py                             # Endpoints: /farmer, /farms, /crop-blocks, /activities
│   │
│   ├── data/                                     # RUNTIME DATA & TEST ASSETS
│   │   ├── sample_leaf.jpg                       # Reference image for automated test runs
│   │   ├── sqlite/                               # SQLite database directory (when configured)
│   │   ├── test_labeled_samples/                 # Ground-truth test images from PlantDoc/PlantVillage
│   │   └── uploads/                              # Persistent storage for user-uploaded leaf photographs
│   │
│   ├── db/                                       # DATABASE LAYER (SQLAlchemy Session & 5 Schemas)
│   │   ├── __init__.py                           # Exposes all models to ensure complete metadata registration
│   │   ├── base.py                               # DeclarativeBase instance with schema naming conventions
│   │   ├── session.py                            # Database engine, connection pooling, and get_db dependency
│   │   │
│   │   ├── migrations/                           # Alembic migration scripts
│   │   │   ├── env.py                            # Alembic migration runtime configuration
│   │   │   └── versions/                         # Versioned migration revision files
│   │   │
│   │   └── models/                               # 5-SCHEMA DATABASE DOMAIN ENTITIES
│   │       ├── __init__.py                       # Aggregates and re-exports all entities
│   │       │
│   │       ├── agronomy/                         # Schema: agronomy
│   │       │   ├── disease_detection.py          # Table: disease_detections (image path, diagnosis, confidence)
│   │       │   └── farm_activity.py              # Table: farm_activities (spray, fertilize, harvest logs)
│   │       │
│   │       ├── core/                             # Schema: core
│   │       │   ├── crop_block.py                 # Table: crop_blocks (variety, tree count, planting date)
│   │       │   ├── farm.py                       # Table: farms (name, latitude, longitude, area, soil type)
│   │       │   ├── farmer_profile.py             # Table: farmer_profiles (phone, experience, preferred language)
│   │       │   ├── iot_device.py                 # Table: iot_devices (device UID, hardware type, status)
│   │       │   └── user.py                       # Table: users (email, hashed password, role, is_active)
│   │       │
│   │       ├── env/                              # Schema: env
│   │       │   ├── soil_sensor_reading.py        # Table: soil_sensor_readings (moisture, temperature, NPK)
│   │       │   └── weather_reading.py            # Table: weather_readings (ambient temp, humidity, rainfall)
│   │       │
│   │       ├── logs/                             # Schema: logs
│   │       │   ├── advisory.py                   # Table: advisories (action recommended, input snapshot, cost)
│   │       │   ├── feedback.py                   # Table: feedbacks (farmer rating, outcome confirmation)
│   │       │   ├── notification.py               # Table: notifications (alert title, priority, read status)
│   │       │   └── system_log.py                 # Table: system_logs (agent execution audit trace)
│   │       │
│   │       └── market/                           # Schema: market
│   │           └── market_price.py               # Table: market_prices (mandi, variety, grade, modal price)
│   │
│   ├── hardware/                                 # IOT HARDWARE GATEWAY & INGESTION
│   │   ├── mqtt_listener.py                      # Subscribes to farm telemetry MQTT topics
│   │   └── router.py                             # Direct REST endpoints for IoT device ingestion
│   │
│   ├── schemas/                                  # PYDANTIC TYPED DATA TRANSFER OBJECTS (DTOs)
│   │   ├── __init__.py                           # Export index
│   │   ├── activity.py                           # FarmActivityCreate, FarmActivityResponse
│   │   ├── advisory.py                           # AdvisoryRequest, AdvisoryResponse
│   │   ├── auth.py                               # UserRegister, UserLogin, TokenResponse
│   │   ├── coordinator.py                        # OrchestrationRequest, OrchestrationResponse
│   │   ├── crop_block.py                         # CropBlockCreate, CropBlockResponse
│   │   ├── diagnosis.py                          # Google AI multimodal diagnosis schemas
│   │   ├── disease.py                            # DiseaseDetectionRequest, DiagnosisResponse
│   │   ├── farm.py                               # FarmCreate, FarmResponse
│   │   ├── farmer.py                             # FarmerProfileCreate, FarmerProfileResponse
│   │   ├── learning.py                           # FeedbackSubmission, QTableInspection
│   │   ├── market.py                             # PriceHistoryQuery, ForecastResponse
│   │   ├── notifying.py                          # NotificationListResponse, MarkReadRequest
│   │   └── weather.py                            # WeatherCurrentResponse, DiseaseRiskResponse
│   │
│   ├── scripts/                                  # UTILITIES & REPRODUCTIVE SCRIPTS
│   │   ├── check_db_connection.py               # Verifies database availability and prints active dialect
│   │   ├── evaluate_vision_model.py              # Evaluates precision, recall, and F1-score across datasets
│   │   ├── load_test.py                          # Simple latency and concurrency load generator
│   │   ├── seed_db.py                            # Seeds demo farmer, farm, crop blocks, and sample readings
│   │   └── sync_plantdoc.py                      # Downloader and preprocessor for PlantDoc benchmark images
│   │
│   └── tests/                                    # AUTOMATED TEST SUITE (82 Passing Pytest Specs)
│       ├── conftest.py                           # Shared fixtures (in-memory test DB, test client, mock images)
│       ├── test_advisory_agent.py                # Tests Gemini advisory prompting and fallback rules
│       ├── test_auth.py                          # Tests user registration, password hashing, and JWT tokens
│       ├── test_coordinator.py                   # Tests priority weight calculations and action synthesis
│       ├── test_core.py                          # Tests farmer, farm, and crop block CRUD endpoints
│       ├── test_diagnosis_agent.py               # Tests Google AI multimodal integration and edge comparison
│       ├── test_e2e_workflow.py                  # Full cycle: User -> Upload -> Diagnose -> Advise -> Feedback
│       ├── test_learning_agent.py                # Tests Q-learning state transitions and reward calculations
│       ├── test_market_agent.py                  # Tests AGMARKNET client and LSTM inference
│       ├── test_notifying_agent.py               # Tests threshold breach alert generation
│       ├── test_vision_agent.py                  # Tests MobileNetV2 image inference and crop validation
│       └── test_weather_agent.py                 # Tests weather risk calculations and ARIMA forecasting
│
├── docs/                                         # DOCUMENTATION, REPORTS & BENCHMARKS
│   ├── AGRICULTURAL_RESOURCES_AND_BENCHMARKS.md  # Official ICAR/KVK reference citations and disease benchmarks
│   ├── api_reference.md                          # Quick API cheat sheet
│   ├── architecture_diagram.png                  # Visual system architecture diagram
│   ├── db_schema.md                              # Schema structure overview
│   ├── MODEL_EVALUATION_REPORT.md                # Quantitative accuracy metrics of vision models
│   ├── PROJECT_UPGRADE_SUMMARY.md                # Detailed log of the Google AI platform upgrade
│   ├── TRAINING_HANDOFF.md                       # Guide for re-training vision models on custom datasets
│   └── training_console_output.txt               # Raw terminal training logs
│
├── firmware/                                     # EMBEDDED IOT HARDWARE CODE (ESP32)
│   ├── platformio.ini                            # PlatformIO build configuration, board definition & libraries
│   ├── README.md                                 # Wiring schematic and sensor calibration guide
│   └── src/                                      # C++ Embedded Source Files
│       ├── main.cpp                              # Setup and recurring telemetry sensor loop
│       ├── oled_display.cpp                      # SSD1306 0.96" OLED driver for in-field readings
│       ├── soil_moisture.cpp                     # Capacitive soil moisture sensor analog reading & calibration
│       └── wifi_mqtt_client.cpp                  # WiFi reconnection and secure MQTT publishing client
│
├── frontend-web/                                 # SINGLE PAGE WEB APPLICATION (React 18 + Vite)
│   ├── .env.example                              # Frontend API base URL configuration (`VITE_API_BASE_URL`)
│   ├── index.html                                # HTML5 root document and viewport metadata
│   ├── package.json                              # Node dependencies, scripts, and build targets
│   ├── vite.config.js                            # Vite dev server configuration and reverse proxy rules
│   │
│   └── src/                                      # REACT APPLICATION SOURCE CODE
│       ├── App.jsx                               # Root application router and layout providers
│       ├── index.css                             # Global styles, Tailwind directives, dark theme tokens
│       ├── main.jsx                              # React DOM root initialization
│       │
│       ├── api/                                  # AXIOS API CLIENT SERVICES
│       │   ├── activity.js                       # Farm activity logging endpoints
│       │   ├── advisory.js                       # Advisory generation endpoints
│       │   ├── auth.js                           # Login and registration endpoints
│       │   ├── client.js                         # Base Axios instance with Bearer token interceptors
│       │   ├── coordinator.js                    # Orchestration trigger endpoints
│       │   ├── disease.js                        # Disease detection & Google AI diagnosis endpoints
│       │   ├── farmer.js                         # Farmer profile and farm management endpoints
│       │   ├── learning.js                       # Feedback submission endpoints
│       │   ├── market.js                         # Commodity price and forecast endpoints
│       │   ├── mockData.js                       # Offline demo fallback datasets
│       │   ├── notifying.js                      # Notification fetch and acknowledge endpoints
│       │   └── weather.js                        # Weather readings and risk index endpoints
│       │
│       ├── assets/                               # Static images, logos, and UI graphics
│       │
│       ├── components/                           # REUSABLE REACT UI COMPONENTS
│       │   ├── FarmSetupModal.jsx                # Onboarding wizard for adding farms and crop plots
│       │   ├── GoogleAIDiagnosis.jsx             # DUAL-ENGINE GOOGLE GEMINI PATHOLOGY DIAGNOSTIC UI
│       │   ├── Navbar.jsx                        # Top navigation bar with farmer profile and notifications
│       │   ├── ProtectedRoute.jsx                # Route guard verifying JWT authentication token
│       │   ├── Sidebar.jsx                       # Navigation drawer linking all 8 agent portals
│       │   └── ui/                               # Modern Bento-Grid & Glassmorphic UI Elements
│       │       ├── bento-card.tsx                # Interactive dashboard cards with hover effects
│       │       └── modern-login-signup.tsx       # Animated authentication cards
│       │
│       ├── context/                              # GLOBAL REACT CONTEXT STATE
│       │   ├── AuthContext.jsx                   # User session, JWT storage, login/logout methods
│       │   └── FarmContext.jsx                   # Active farm, selected crop block, and sensor state
│       │
│       └── pages/                                # DEDICATED AGENT PORTALS & VIEWS
│           ├── ActivityLog.jsx                   # Farmer logbook for spraying, fertilizer, harvesting
│           ├── Advisory.jsx                      # Agronomic advisory panel with LLM-generated recommendations
│           ├── Dashboard.jsx                     # Master overview synthesizing metrics from all 8 agents
│           ├── DiseaseDetection.jsx              # AI Plant Pathology page with dual local/cloud engine
│           ├── FarmerProfile.jsx                 # Farm configuration, user preferences, and land registry
│           ├── Login.jsx                         # Farmer authentication portal
│           ├── Market.jsx                        # Mandi commodity prices and LSTM price forecast charts
│           ├── Register.jsx                      # New farmer registration screen
│           └── Weather.jsx                       # Microclimate conditions, rainfall, and fungal risk radar
│
├── infra/                                        # INFRASTRUCTURE & DEPLOYMENT
│   ├── deployment_notes.md                       # Production deployment guide
│   └── postgres_init.sql                         # SQL script initializing the 5 PostgreSQL schemas
│
└── mobile-app/                                   # MOBILE APPLICATION (React Native / Expo Starter)
    ├── assets/                                   # Mobile app splash screens and icons
    └── src/                                      # Mobile React Native navigation and screens
        ├── api/                                  # Mobile API client
        └── screens/                              # Mobile disease capture and dashboard screens
```

---

## 4. Multi-Agent System Architecture (The 8 Autonomous Agents)

Areca-Agent functions as a **cooperative multi-agent system**, where each agent operates with autonomous domain logic while continuously exchanging telemetry and inferences through the **Coordinator Agent**.

```
                           ┌───────────────────────────┐
                           │   FARMER / CLIENT UI      │
                           │  (Web / Mobile / IoT)     │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │   COORDINATOR AGENT       │
                           │  (Priority Orchestrator)  │
                           └─────────────┬─────────────┘
                                         │
        ┌───────────────┬────────────────┼────────────────┬──────────────┐
        ▼               ▼                ▼                ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ VISION AGENT │ │  DIAGNOSIS   │ │ADVISORY AGENT│ │WEATHER AGENT │ │ MARKET AGENT │
│ (Edge CNN /  │ │    AGENT     │ │(Gemini LLM / │ │ (ARIMA /     │ │ (LSTM Mandi  │
│ MobileNetV2) │ │ (Google AI)  │ │   IPM Cache) │ │ Disease Risk)│ │ Forecasting) │
└───────┬──────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
        │               │                │                │                │
        └───────────────┴────────────────┼────────────────┴────────────────┘
                                         ▼
                           ┌───────────────────────────┐
                           │      LEARNING AGENT       │
                           │  (Q-Learning Feedback)    │
                           └─────────────┬─────────────┘
                                         │
                                         ▼
                           ┌───────────────────────────┐
                           │      NOTIFYING AGENT      │
                           │   (Threshold Alerts)      │
                           └───────────────────────────┘
```

### 4.1 Vision Agent (Edge Deep Learning)
- **File Location**: `backend/agents/vision/`
- **Primary Modules**: `inference.py`, `model.py`, `preprocess.py`, `crop_validator.py`, `advisory_db.py`
- **Weights Location**: `backend/agents/vision/weights/`
- **Role & Stack**:
  - Serves as the first-line, low-latency edge classifier.
  - Pre-validates images via `crop_validator.py` to prevent processing non-plant images (e.g., cars, faces, random objects).
  - Employs **MobileNetV2** (fine-tuned on 38 classes of PlantVillage/PlantDoc) stored in fast zero-copy `safetensors` format.
  - Also includes a specialized PyTorch CNN (`arecanut_cnn.pt`) specifically tuned for arecanut leaf spot, koleroga (fruit rot), and yellow leaf disease.
  - Extracts visual feature embeddings and compares them using cosine similarity (`similarity.py`) against known reference vectors.

### 4.2 Diagnosis Agent (Google AI Multimodal + Bayesian Belief Network)
- **File Location**: `backend/agents/diagnosis/`
- **Primary Modules**: `google_ai.py`, `bayesian.py`, `router.py`
- **Role & Stack**:
  - Upgraded with Google's official `google-genai` Python SDK (v2.33.0).
  - Uses Google's latest multimodal models:
    - Primary: `gemini-3.1-flash-lite-preview` (high-throughput, ultra-low latency, multimodal)
    - Fallback: `gemini-3-flash-preview` (high-reasoning, comprehensive pathology)
  - Features:
    1. **Visual Symptom Breakdown**: Pinpoints lesion color, concentric rings, chlorotic halos, pattern, and stage.
    2. **Differential Diagnosis**: Returns primary diagnosis + 2 alternative candidate diseases, detailing the specific clinical factors favoring or questioning each diagnosis.
    3. **Edge CNN Cross-Verification**: Compares the local edge prediction with Gemini's diagnosis, calculating agreement levels (`high`, `moderate`, `divergent`) and providing actionable guidance.
    4. **Bayesian Belief Network (`bayesian.py`)**: Fuses visual probabilities with environmental conditions (temperature, humidity, rainfall) and tree age to compute posterior probabilities:
       $$P(\text{Disease} \mid \text{Vision}, \text{Weather}, \text{Age}) \propto P(\text{Vision} \mid \text{Disease}) \cdot P(\text{Weather} \mid \text{Disease}) \cdot P(\text{Disease})$$
    5. **Search Grounding Rate-Limit Fallback**: If the Google Search Grounding tool reaches API quota limits (HTTP 429), the engine automatically falls back to structured multimodal JSON generation, seamlessly injecting verified academic monographs from ICAR, TNAU, and Cornell Agricultural Extension.

### 4.3 Advisory Agent (Agronomic Guidance & LLM Cache)
- **File Location**: `backend/agents/advisory/`
- **Primary Modules**: `gemini_client.py`, `prompts.py`, `cache.py`, `rule_based_fallback.py`
- **Role & Stack**:
  - Generates comprehensive farm management protocols based on validated diagnoses.
  - Implements **SHA256 Request Caching (`cache.py`)**: Hashes the diagnostic input snapshot (crop, disease, severity, tree age, soil moisture). If an identical request was processed recently, it returns the cached advisory in under 5ms without incurring LLM API costs.
  - When offline or when API limits are reached, the agent triggers `rule_based_fallback.py`, serving certified ICAR-approved pesticide dosages, bio-agent spray schedules, and fertilizer guidelines.

### 4.4 Coordinator Agent (Priority Decision Engine)
- **File Location**: `backend/agents/coordinator/`
- **Primary Modules**: `orchestrator.py`, `weights.py`, `router.py`
- **Role & Stack**:
  - The central nervous system of BharatCrop AI.
  - Queries all sub-agents and applies a weighted multi-criteria decision matrix (`weights.py`):
    - **Crop Health / Visual Pathology**: `35%`
    - **Weather & Microclimate Disease Risk**: `30%`
    - **Soil Moisture & Crop Phenological Stage**: `20%`
    - **Market Economic Opportunity**: `15%`
  - Resolves conflicting actions (e.g., *“Fertilizer recommended by Agronomy”* vs. *“Heavy rainfall forecast by Weather Agent”* $\rightarrow$ Coordinator postpones application to prevent nutrient runoff and financial loss).

### 4.5 Weather Agent (Microclimate & Disease Risk)
- **File Location**: `backend/agents/weather/`
- **Primary Modules**: `api_client.py`, `arima_model.py`, `risk_score.py`, `fallback_model.py`
- **Role & Stack**:
  - Connects to live meteorological APIs (Open-Meteo / OpenWeatherMap) using farm GPS coordinates.
  - Uses an **ARIMA (Auto-Regressive Integrated Moving Average)** statistical model (`arima_model.py`) to forecast short-term temperature and relative humidity trends.
  - Computes a continuous **Fungal & Bacterial Disease Proliferation Risk Score (`risk_score.py`)**: Evaluates prolonged leaf wetness (RH > 85%, temp 22°C–28°C) to proactively warn farmers before sporulation occurs.

### 4.6 Market Agent (LSTM Mandi Price Forecasting)
- **File Location**: `backend/agents/market/`
- **Primary Modules**: `data_gov_client.py`, `lstm_model.py`, `train.py`, `fallback_model.py`
- **Role & Stack**:
  - Integrates with Open Government Data (Data.gov.in) to ingest daily APMC Mandi wholesale commodity prices across Karnataka, Kerala, and pan-India markets.
  - Runs a **PyTorch Long Short-Term Memory (LSTM)** neural network (`lstm_model.py`) to predict 7-day modal price trajectories.
  - Recommends the optimal selling window (e.g., *“Hold produce: prices predicted to appreciate by 4.2% over next 5 days”*).

### 4.7 Learning Agent (Q-Learning Feedback Optimization)
- **File Location**: `backend/agents/learning/`
- **Primary Modules**: `q_learning.py`, `feedback_store.py`, `router.py`
- **Role & Stack**:
  - Provides a closed-loop reinforcement learning mechanism.
  - Farmers submit feedback on whether an advisory successfully cured the disease or improved yield.
  - Updates the state-action value table ($Q$-table) using the Bellman equation:
    $$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$$
  - Over time, the system favors interventions that yield the highest verified recovery rates under specific soil and climate states.

### 4.8 Notifying Agent (Threshold Monitoring & Alerts)
- **File Location**: `backend/agents/notifying/`
- **Primary Modules**: `monitoring.py`, `notifications.py`, `router.py`
- **Role & Stack**:
  - Background daemon that continuously evaluates sensor streams and risk metrics against safety thresholds.
  - Generates high-priority push notifications and UI alerts for:
    - Critical disease detection
    - Severe soil moisture deficit (drought stress)
    - Fungal outbreak microclimate risk warnings
    - Favorable commodity market price spikes

---

## 5. AI, Deep Learning & Statistical Models

| Model Name | Type / Architecture | Input Dimensions | Checkpoint / Weights File | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Google Gemini 3 Multimodal** | Cloud Vision-Language Model (`gemini-3.1-flash-lite-preview`) | High-res RGB (JPEG/PNG/WebP) | Cloud API (`google-genai` SDK) | Deep plant pathology, differential diagnosis, lesion symptom extraction, 3-pillar IPM. |
| **Multi-Crop MobileNetV2** | Lightweight Deep CNN (`torchvision` / `safetensors`) | $3 \times 224 \times 224$ (Normalized) | `backend/agents/vision/weights/multi_crop_mobilenetv2/model.safetensors` (9.2 MB) | On-device 38-class plant disease classification covering Apple, Tomato, Corn, Potato, Grape, etc. |
| **Arecanut Custom CNN** | Custom PyTorch 4-layer Convolutional Network | $3 \times 224 \times 224$ | `backend/agents/vision/weights/arecanut_cnn.pt` (10.4 MB) | Specialized local edge diagnosis for Arecanut Koleroga, Yellow Leaf, and Leaf Spot. |
| **Market Price LSTM** | 2-layer Recurrent Neural Network (PyTorch LSTM) | 30-day sequence of normalized daily modal prices | Runtime initialized / `backend/agents/market/lstm_model.py` | 7-day ahead commodity wholesale price forecasting. |
| **Weather ARIMA** | Classical Time-Series Statistical Model | Hourly/daily temperature & humidity lags | Runtime fitted / `backend/agents/weather/arima_model.py` | Microclimate trend extrapolation and sensor anomaly detection. |
| **Bayesian Disease Network** | Directed Acyclic Graph (DAG) with Conditional Probability Tables | Vision confidence, humidity, temperature, crop age | Probabilistic logic / `backend/agents/diagnosis/bayesian.py` | Multi-modal confidence fusion and false-positive reduction. |
| **Advisory Q-Learning** | Model-Free Reinforcement Learning ($Q$-table) | Discrete State (Crop Stage, Severity, Moisture) $\times$ Actions | Runtime updated / `backend/agents/learning/q_learning.py` | Continuous optimization of recommended treatments based on farmer feedback. |

---

## 6. Database Schema & Entity Relationship Model

The database is structured into **5 logical domains**, configured to run seamlessly on SQLite for local development (`areca_agent.db`) and PostgreSQL for multi-tenant production deployments:

```
┌────────────────────────────────────────────────────────────────────────┐
│                         5-SCHEMA DATABASE MODEL                        │
└────────────────────────────────────────────────────────────────────────┘

  [core]
  ├── users (id, email, hashed_password, role, is_active, created_at)
  ├── farmer_profiles (id, user_id, phone, experience_years, preferred_language)
  ├── farms (id, farmer_id, name, latitude, longitude, total_area, soil_type)
  ├── crop_blocks (id, farm_id, variety, planting_date, tree_count, irrigation_type)
  └── iot_devices (id, farm_id, crop_block_id, device_uid, hardware_type, status)

  [agronomy]
  ├── disease_detections (id, crop_block_id, image_path, primary_diagnosis,
  │                       confidence, differential_diagnoses, raw_response, created_at)
  └── farm_activities (id, crop_block_id, activity_type, product_used, dosage, notes)

  [env]
  ├── weather_readings (id, farm_id, temperature, humidity, rainfall, wind_speed, recorded_at)
  └── soil_sensor_readings (id, iot_device_id, moisture_pct, soil_temp, npk_raw, recorded_at)

  [market]
  └── market_prices (id, commodity, mandi_name, state, min_price, max_price, modal_price, date)

  [logs]
  ├── advisories (id, detection_id, action_recommended, input_snapshot, ipm_protocol, cost)
  ├── feedbacks (id, advisory_id, rating, outcome_cured, farmer_notes, submitted_at)
  ├── notifications (id, user_id, title, message, priority, is_read, created_at)
  └── system_logs (id, agent_name, execution_time_ms, status, error_details, created_at)
```

---

## 7. Frontend Web Architecture (React 18 + Vite)

The frontend is a modern, responsive Single Page Application (SPA) designed to deliver instant visual feedback, rich glassmorphic aesthetics, and accessibility for agricultural field operators.

### Key Frontend Portals (`frontend-web/src/pages/`):
1. **`Dashboard.jsx`**: Master command center presenting live sensor feeds, weather risk gauges, recent diagnosis logs, and quick action cards.
2. **`DiseaseDetection.jsx`**: Dual-engine plant pathology laboratory:
   - File drag-and-drop & live camera capture.
   - Client-side crop validation.
   - Dual-engine toggle: Runs local MobileNetV2 edge detection alongside Google Gemini AI.
3. **`GoogleAIDiagnosis.jsx`**: Dedicated component visualizing:
   - Live Gemini connection health badge.
   - Primary disease card with severity indicator and confidence meter.
   - Side-by-side **Differential Diagnosis** cards detailing clinical evidence.
   - **Visual Symptom Breakdown** grid (lesion color, chlorotic halo, pattern, stage).
   - **3-Pillar IPM Tabbed View** (Organic/Bio, Chemical with dosage & safety, Agronomic practices).
   - Edge CNN vs. Cloud AI agreement cross-check banner.
4. **`Weather.jsx`**: Real-time microclimate dashboard, 7-day forecast cards, and fungal proliferation radar.
5. **`Market.jsx`**: Interactive APMC mandi commodity price charts and LSTM 7-day price forecasts.
6. **`Advisory.jsx`**: Chronological log of farm advisories with treatment completion toggles.
7. **`ActivityLog.jsx`**: Digital farm ledger for tracking chemical applications, irrigation cycles, and yields.
8. **`FarmerProfile.jsx`**: Plot configuration, GPS coordinates, crop block age, and preference settings.

---

## 8. IoT Firmware & Hardware Telemetry (ESP32)

- **Hardware Platform**: ESP-WROOM-32 Microcontroller
- **Location**: `firmware/`
- **Sensors**:
  - Capacitive Soil Moisture Sensor v1.2 (corrosion-resistant analog output)
  - DHT22 / SHT31 (high-precision ambient temperature and relative humidity)
  - 0.96" I2C SSD1306 OLED Display (field visual readout)
- **Protocol**: MQTT over WiFi (TLS supported)
- **Telemetry Payload (JSON)**:
  ```json
  {
    "device_uid": "ESP32_FARM_01",
    "crop_block_id": 1,
    "soil_moisture_pct": 42.5,
    "temperature_c": 27.8,
    "humidity_pct": 84.1,
    "battery_mv": 3950
  }
  ```
- **Firmware Files**:
  - `main.cpp`: Main setup and sensor reading scheduler.
  - `soil_moisture.cpp`: Non-linear ADC calibration curve.
  - `oled_display.cpp`: Formats and displays readings locally on the field device.
  - `wifi_mqtt_client.cpp`: Auto-reconnecting WiFi and MQTT client publishing to `farm/sensors/telemetry`.

---

## 9. REST API Endpoints & Routing Guide

All API endpoints are hosted by FastAPI and documented interactively at `http://127.0.0.1:8000/docs`.

### Core Diagnostics & Vision Endpoints:
| Method | Endpoint | Description | Request Body / Params |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/diagnose` | **Google Gemini Multimodal Diagnosis** (Dual-Engine Analysis) | `multipart/form-data`: `file`, optional `crop_hint` |
| `POST` | `/api/v1/diagnose` | Direct alias for `/api/diagnose` | `multipart/form-data`: `file`, optional `crop_hint` |
| `GET` | `/api/diagnose/status`| Returns Google AI SDK availability and active model name | None |
| `POST` | `/api/v1/vision/detect` | Local edge CNN disease detection (MobileNetV2 / Arecanut CNN) | `multipart/form-data`: `file` |
| `POST` | `/api/v1/vision/diagnose`| Edge CNN classification with full static monograph protocol | `multipart/form-data`: `file` |

### Multi-Agent Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/coordinator/orchestrate` | Triggers multi-agent evaluation for a farm plot |
| `POST` | `/api/v1/advisory/generate` | Generates agronomic advisory using Gemini or rule fallback |
| `GET` | `/api/v1/weather/current` | Fetches live meteorological conditions for coordinates |
| `GET` | `/api/v1/weather/risk` | Calculates fungal and bacterial disease risk indices |
| `GET` | `/api/v1/market/prices` | Queries recent APMC mandi commodity wholesale rates |
| `GET` | `/api/v1/market/forecast` | Returns 7-day modal price predictions from the LSTM model |
| `POST` | `/api/v1/learning/feedback` | Submits farmer treatment outcome to update $Q$-learning table |
| `GET` | `/api/v1/notifying/alerts` | Returns active notifications and alerts for the user |

### Farm Domain & Auth Endpoints:
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Creates a new farmer account with salted bcrypt password |
| `POST` | `/api/v1/auth/login` | Authenticates user and issues a signed JWT access token |
| `GET` | `/api/v1/farms` | Lists all farms registered to the authenticated user |
| `POST` | `/api/v1/farms` | Creates a new farm profile with GPS boundaries |
| `GET` | `/api/v1/crop-blocks` | Retrieves all crop blocks with plantation age and tree counts |
| `POST` | `/api/v1/activities` | Logs a farm management event (spraying, fertilizer, harvest) |

---

## 10. Configuration & Environment Variables

The system loads settings via Pydantic (`backend/config.py`) from `backend/.env`.

```ini
# Environment Mode
ENVIRONMENT=development
LOG_LEVEL=INFO

# Security & Authentication
SECRET_KEY=development-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Configuration (Default: Zero-dependency local SQLite)
DATABASE_URL=sqlite:///./areca_agent.db

# External APIs (Google Gen AI SDK v2.x)
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_DAILY_BUDGET_CAP=100

# Open Government Data API
DATA_GOV_IN_API_KEY=YOUR_DATA_GOV_IN_API_KEY_HERE

# Vision Engine Settings
VISION_BACKEND=multicrop
VISION_CONFIDENCE_THRESHOLD=0.48
MAX_UPLOAD_IMAGE_SIZE_BYTES=15728640
```

> **Security Note**: `backend/.env` is strictly excluded from version control via `.gitignore` to prevent secret leakage.

---

## 11. Execution, Testing & Deployment

### Quick Windows Startup (One-Click Launchers):
1. **Backend Server**: Double-click `run_backend.bat`  
   - Launches Uvicorn on `http://127.0.0.1:8000` with hot-reload enabled.
   - Automatically initializes SQLite database tables and seeds demo farmer data.
2. **Frontend UI**: Double-click `run_frontend.bat`  
   - Launches Vite dev server on `http://localhost:5173`.

### Manual CLI Startup:
```powershell
# 1. Start Backend Server
cd Areca-Agent-main
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start Frontend Dev Server (in a new terminal)
cd Areca-Agent-main/frontend-web
npm run dev
```

### Running Automated Test Suite:
```powershell
cd Areca-Agent-main
pytest -v
# Output: 82 passed in 10.42s
```

### Production Docker Deployment:
```powershell
cd Areca-Agent-main
docker-compose up -d --build
```
This launches:
- `areca_postgres`: PostgreSQL 16 container on port `5432` with pre-initialized schemas (`infra/postgres_init.sql`).
- `areca_backend`: FastAPI backend container on port `8000`.

---
*Document Version: 2.1 — All rights reserved © 2026 BharatCrop AI / Areca-Agent Engineering Team.*
