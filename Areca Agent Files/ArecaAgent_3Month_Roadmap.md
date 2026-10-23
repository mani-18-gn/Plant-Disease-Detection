# ArecaAgent — 3-Month Implementation Roadmap

**Team:** Samarth N K, Sathwik Hebbar P, Suchesh S Shetty, Vihar A C
**Guide:** Dr. Thyagaraju G S
**Goal:** Fully working multi-agent system with web dashboard + mobile app + ESP32 hardware, LLM-powered Advisory Agent (Gemini API)

---

## Architecture Note: Where Gemini Fits

Keep your specialized ML models doing what they're good at, and use Gemini as the **reasoning/orchestration layer**, not a replacement for them:

| Agent | Model | Why |
|---|---|---|
| Vision Agent | CNN (own-trained/transfer learning) | Gemini isn't reliable for fine-grained disease classification on a niche crop |
| Weather Agent | ARIMA / weather API | Deterministic, no LLM needed |
| Market Agent | LSTM | Deterministic, no LLM needed |
| Diagnosis Agent | Bayesian inference | Simple probability math |
| **Advisory Agent** | **Gemini API** | Turns structured outputs from all agents into natural-language, farmer-friendly advice |
| **Coordinator Agent** | **Gemini API (function calling) or rule engine** | Gemini can orchestrate tool calls to other agents if you use function calling; otherwise keep it rule-based for reliability |
| Learning Agent | Q-learning (lightweight) | Can be simplified to a feedback-score store if time is tight |
| Notifying/Monitoring | Backend services | No ML needed |

This keeps your system technically defensible (you're not just wrapping a chatbot) while giving you a genuinely useful LLM integration for advisory text generation.

---

## Month 1 — Core Agents + Infrastructure

**Week 1: Setup & Data Pipeline**
- Set up FastAPI backend skeleton, Python 3.11+ (note: 3.14 in your report may not have full library support yet — recommend 3.11/3.12 for stability with TensorFlow/PyTorch)
- Set up PostgreSQL/MongoDB for the 5 databases (Crop Health, Env, Market, User, Logs)
- Download and clean Kaggle Arecanut dataset; plan local farm image collection
- Get Gemini API key (Google AI Studio), set up billing/quota limits
- Get data.gov.in API access for market prices; get OpenWeatherMap/NOAA API key

**Week 2–3: Vision Agent**
- Preprocess images (224×224, augmentation: rotation, zoom, brightness)
- Fine-tune a transfer-learning CNN (MobileNetV2/ResNet, pretrained on PlantVillage or ImageNet)
- Train, validate, target >85% accuracy on your classes
- Wrap as an inference API endpoint (`/detect-disease`)

**Week 4: Weather Agent + Diagnosis Agent**
- Integrate live weather API + build ARIMA model on historical data (or start simpler with a moving-average/threshold model if ARIMA underperforms on limited data — be ready to simplify)
- Implement Bayesian validation logic combining CNN confidence + weather favorability
- **Milestone:** Vision + Weather + Diagnosis agents working end-to-end via API calls, tested with Postman/curl

---

## Month 2 — Remaining Agents + Frontend

**Week 5: Market Agent**
- Pull historical arecanut price data from data.gov.in
- Train LSTM (60-day window → 7-day forecast), evaluate with MAPE
- If data volume is too small for LSTM to converge well, have a fallback (SARIMA or simple regression) — don't let this block the timeline

**Week 6: Advisory + Coordinator Agents (Gemini Integration)**
- Design a structured JSON schema that all agents output into (disease, confidence, weather risk, price trend, etc.)
- Prompt-engineer Gemini to convert this JSON into farmer-friendly, prioritized advisory text (Urgent/High/Medium/Low, matching your priority matrix)
- Implement Coordinator Agent to call each agent, aggregate weighted outputs (35/30/20/15 as per your table), and pass to Advisory Agent
- Add guardrails: cache/validate Gemini output, have a rule-based fallback if the API fails or returns malformed advice

**Week 7–8: Web Dashboard**
- Build frontend (React recommended) matching your mockups: Login, Home/Dashboard, Weather, Market, Disease Detection, Advisory
- Connect to backend REST APIs
- Implement JWT authentication
- **Milestone:** Farmer can log in, upload a leaf photo, and see disease + weather + market + advisory in one dashboard (web only at this point)

---

## Month 3 — Mobile App, Hardware, Testing, Docs

**Week 9: Mobile App**
- Build with Flutter or React Native (share API layer with the web dashboard) — this is the fastest path to a working cross-platform app in limited time
- Port core screens: login, dashboard, disease detection (camera upload), alerts

**Week 10: Hardware Integration**
- Flash ESP32 with soil moisture sensor + OLED display firmware
- Push sensor readings to backend via WiFi/MQTT/HTTP
- Display basic status (moisture %, alerts) on the OLED
- Note: this is the highest-risk item for a 4-person team in one week — start ESP32 firmware work earlier (parallel to Week 5–6) if anyone on the team has embedded experience, rather than leaving it fully sequential

**Week 11: Learning Agent + Notifying/Monitoring + End-to-End Testing**
- Implement feedback capture (star ratings) and simple Q-value/score updates
- Wire up push/SMS notifications for Urgent/High alerts
- Full integration testing: image upload → disease detection → weather validation → advisory → notification, across web + app
- Bug fixing, load testing on key endpoints

**Week 12: Documentation & Presentation**
- Finalize Phase 2 report (results, screenshots, accuracy metrics, limitations)
- Prepare demo script and slide deck
- Rehearse presentation, prepare for Q&A on algorithm choices (be ready to justify ARIMA/LSTM vs. simpler baselines if the panel pushes back)

---

## Risk Flags to Watch

1. **Dataset size** — your Kaggle dataset + local farm images may be small for CNN and especially LSTM; plan augmentation and have simpler fallback models ready.
2. **ESP32/hardware** — physically dependent on component availability; order parts in Week 1, not Week 10.
3. **Gemini API costs/rate limits** — set a budget cap and request-per-user limit early; cache advisory responses where inputs haven't changed.
4. **4 people, 7+ agents** — assign one agent-cluster per person (e.g., Vision+Diagnosis, Weather+Market, Advisory+Coordinator+Gemini, Frontend+Mobile) so nothing is a bottleneck on one person.
5. **Python 3.14** — verify your ML libraries (TensorFlow/PyTorch/scikit-learn) actually support it before committing; downgrade to 3.11/3.12 if not.

---

*Roadmap derived from the ArecaAgent Phase 1 report (SDM Institute of Technology, 2025-2026).*
