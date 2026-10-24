import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.db.session import engine
from backend.db.base import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Import all models to ensure schema registration before table creation
import backend.db.models  # noqa

# Explicit direct router imports (decoupled from package __init__.py files)
from backend.auth.router import router as auth_router
from backend.core.router import router as core_router
from backend.agents.vision.router import router as vision_router
from backend.agents.diagnosis.router import router as diagnosis_router
from backend.agents.weather.router import router as weather_router
from contextlib import asynccontextmanager
from backend.agents.market.router import router as market_router
from backend.agents.advisory.router import router as advisory_router
from backend.agents.coordinator.router import router as coordinator_router
from backend.agents.learning.router import router as learning_router
from backend.agents.notifying.router import router as notifying_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables are created and warm up ML models asynchronously."""
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        try:
            from backend.db.session import SessionLocal
            from backend.db.models.core.user import User
            with SessionLocal() as db:
                if not db.query(User).first():
                    from backend.scripts.seed_db import seed
                    seed()
        except Exception as e:
            logger.warning(f"Auto-seed check: {e}")

    import threading

    def _bg_warmup():
        backend = getattr(settings, "VISION_BACKEND", "multicrop").lower()
        try:
            if backend == "multicrop":
                from backend.agents.vision.inference import warmup_vision_model
                warmup_vision_model()
                logger.info("Multicrop MobileNetV2 warmed up successfully.")
            elif backend == "keras":
                from backend.agents.vision.keras_inference import warmup_keras_model
                warmup_keras_model()
                logger.info("Keras model warmed up successfully.")
            elif backend == "pytorch":
                from backend.agents.vision.inference import get_pytorch_model
                get_pytorch_model()
                logger.info("PyTorch arecanut model loaded.")
        except Exception as e:
            logger.warning(f"Vision model warmup skipped: {e}")

    threading.Thread(target=_bg_warmup, daemon=True, name="model_warmup").start()
    yield


app = FastAPI(
    title="ArecaAgent Backend API",
    description="FastAPI monorepo for ArecaAgent multi-agent system (PostgreSQL 5-schema architecture)",
    version="0.2.0",
    lifespan=lifespan,
)

# Enable CORS for frontend applications (local dev, LAN access, and standard ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/", tags=["Health Check"])
@app.get("/health", tags=["Health Check"])
@app.get("/api/v1/health", tags=["Health Check"])
def root():
    return {
        "status": "healthy",
        "app": "ArecaAgent Monorepo Backend API",
        "version": "0.2.0",
        "environment": settings.ENVIRONMENT
    }


# Mount Routers under /api/v1
api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(core_router, prefix=api_prefix)
app.include_router(vision_router, prefix=api_prefix)
app.include_router(diagnosis_router, prefix=api_prefix)
app.include_router(weather_router, prefix=api_prefix)
app.include_router(market_router, prefix=api_prefix)
app.include_router(advisory_router, prefix=api_prefix)
app.include_router(coordinator_router, prefix=api_prefix)
app.include_router(learning_router, prefix=api_prefix)
app.include_router(notifying_router, prefix=api_prefix)

# Direct root-level and v1 aliases for Google-Powered Plant Disease Diagnosis (Section 7)
from backend.agents.diagnosis.router import diagnose_plant, google_ai_status
app.add_api_route("/api/diagnose", diagnose_plant, methods=["POST"], tags=["Diagnosis Agent"])
app.add_api_route("/api/v1/diagnose", diagnose_plant, methods=["POST"], tags=["Diagnosis Agent"])
app.add_api_route("/api/diagnose/status", google_ai_status, methods=["GET"], tags=["Diagnosis Agent"])

# Mount Static Uploads directory for image access
uploads_dir = Path(__file__).resolve().parent / "data" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
app.mount("/api/v1/uploads", StaticFiles(directory=str(uploads_dir)), name="api_uploads")

