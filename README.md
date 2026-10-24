# 🌱 Plant Disease Detection & Agricultural Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF.svg)](https://vitejs.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, multi-crop plant disease intelligence and agricultural management platform. The system combines deep neural computer vision, Bayesian diagnostic validation, microclimate weather tracking, regional mandi market intelligence, and multi-agent expert agronomy advisories to assist farmers and agricultural researchers.

---

## 🌟 Key Features

1. **Multi-Crop Computer Vision Disease Detection**:
   - Deep learning vision engine powered by **MobileNetV2** and **PyTorch / Safetensors**.
   - Supports **38+ plant disease classes** spanning major agricultural crops:
     - **Tomato**: Late Blight, Early Blight, Leaf Mold, Septoria, Spider Mites, Target Spot, Yellow Leaf Curl, Mosaic Virus, Healthy.
     - **Potato**: Early Blight, Late Blight, Healthy.
     - **Corn (Maize)**: Common Rust, Northern Leaf Blight, Gray Leaf Spot, Healthy.
     - **Grape**: Black Rot, Esca (Black Measles), Leaf Blight, Healthy.
     - **Apple**: Apple Scab, Black Rot, Cedar Apple Rust, Healthy.
     - **Arecanut (Betelnut)**: Koleroga (Fruit Rot), Yellow Leaf Disease, Stem Bleeding, Healthy.
     - **Bell Pepper, Peach, Strawberry, Cherry, and more**.
   - Dual-mode inference: High-performance local neural model with zero-configuration fallback.

2. **Google-Powered Multimodal AI & Grounded Diagnosis (Gemini 2.5 Flash)**:
   - Multimodal plant pathology diagnosis powered by the official `google-genai` SDK (`gemini-2.5-flash`, with fallback to `gemini-2.0-flash` and `gemini-1.5-flash`).
   - Non-plant and foliage plausibility checks: automatically rejects non-plant subjects safely.
   - Grounded agricultural research: integrates Google Search grounding metadata along with ICAR and University extension monographs.
   - Dual-engine co-existence: operates independently alongside the local MobileNetV2 neural vision model for cross-verification.
   - Dedicated REST APIs: `POST /api/diagnose` and `GET /api/diagnose/status`.

3. **Bayesian Diagnosis & Advisory Synthesis**:
   - Integrates neural visual confidence with environmental parameters (temperature, humidity, rainfall).
   - Generates actionable, evidence-based chemical, organic, and cultural treatment recommendations with dosage guidelines.

3. **Multi-Agent Architecture**:
   - **Vision Agent**: Image validation, normalization, and classification.
   - **Diagnosis Agent**: Confidence scoring, symptom correlation, and severity assessment.
   - **Weather Agent**: Microclimate telemetry, weather forecasting, and risk indices.
   - **Market Agent**: Real-time regional Mandi commodity pricing and market trends.
   - **Advisory Agent**: Multilingual farmer advisories (English, Kannada, Hindi).
   - **Coordinator Agent**: Cross-agent decision synthesis.

4. **Multi-Schema Database Architecture**:
   - PostgreSQL / SQLite with 5 decoupled domain schemas:
     - `core`: Farmers, farms, perennial crop blocks, IoT sensors.
     - `agronomy`: Historical disease detections and farm management activities (spraying, fertilizer, irrigation).
     - `env`: Sensor telemetry and microclimate readings.
     - `market`: Regional APMC mandi pricing.
     - `logs`: Notification queue, advisory audit logs, and feedback loops.

5. **Modern Reactive Web Dashboard**:
   - Built with **React 18**, **Vite**, **Tailwind/Modern CSS**, and responsive UI.
   - Interactive diagnosis upload studio, sample image presets, live weather widgets, interactive charts, and farm management.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.11, 3.12, 3.14)
- **Node.js 18+** & **npm**

### Option A: One-Click Launch (Windows)
1. Double-click `run_backend.bat` to launch the FastAPI backend.
2. Double-click `run_frontend.bat` to launch the React frontend.
3. Open your browser at **[http://localhost:5173](http://localhost:5173)**.

---

### Option B: Manual Setup

#### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/mani-18-gn/Plant-Disease-Detection.git
cd Plant-Disease-Detection

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables (optional for Google AI multimodal pathology)
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your-api-key-here

# Start FastAPI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive Swagger API docs will be available at: **`http://127.0.0.1:8000/docs`**

#### 2. Frontend Setup
```bash
# In a new terminal, navigate to frontend-web
cd frontend-web

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

Access the frontend application at: **`http://localhost:5173`**

---

## 🔑 Demo Credentials

A pre-seeded demonstration account is available for instant testing:
- **Username**: `farmer_demo` *(or click the **"Quick Demo Login"** button on the login screen)*
- **Password**: `password123`

---

## 🧪 Running Automated Tests

Run the full automated test suite covering all agent modules:
```bash
pytest backend/tests
```
All **42+ tests** validate vision inference, authentication, Bayesian diagnosis, coordinator synthesis, and database operations.

---

## 📂 Repository Structure

```
Plant-Disease-Detection/
├── backend/
│   ├── main.py                  # FastAPI application entry point & CORS configuration
│   ├── config.py                # Pydantic environment settings
│   ├── auth/                    # JWT authentication & password hashing
│   ├── core/                    # Farmer profile, farm, and crop block CRUD APIs
│   ├── db/                      # SQLAlchemy models organized across 5 domain schemas
│   ├── agents/
│   │   ├── vision/              # Deep learning model inference & sample images
│   │   ├── diagnosis/           # Bayesian diagnostic validation
│   │   ├── weather/             # Weather telemetry & risk scoring
│   │   ├── market/              # APMC mandi pricing
│   │   ├── advisory/            # Treatment and agronomic advisory generation
│   │   ├── coordinator/         # Multi-agent decision synthesis
│   │   ├── learning/            # Farmer feedback & reinforcement loops
│   │   └── notifying/           # Notification dispatch service
│   ├── scripts/                 # Database seed & migration utilities
│   └── tests/                   # Pytest test suite (42 unit & integration tests)
├── frontend-web/
│   ├── src/
│   │   ├── pages/               # DiseaseDetection, Dashboard, Weather, Market, Advisory
│   │   ├── components/          # Reusable UI components & navigation
│   │   ├── context/             # AuthContext & FarmContext state providers
│   │   └── api/                 # Axios API clients
│   ├── vite.config.js           # Vite dev server & proxy settings
│   └── package.json
├── firmware/                    # ESP32 IoT sensor telemetry firmware
├── docs/                        # Architecture specs & training documentation
├── run_backend.bat              # One-click Windows backend launcher
├── run_frontend.bat             # One-click Windows frontend launcher
└── pytest.ini                   # Pytest configuration
```

---

## 📄 License
This project is licensed under the MIT License — see the LICENSE file for details.
