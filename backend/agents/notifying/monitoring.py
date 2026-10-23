import time
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
import httpx

from backend.db.models.logs.system_log import SystemLog, LogLevel
from backend.config import settings

logger = logging.getLogger(__name__)


def log_system_event(
    db: Session,
    service: str,
    level: LogLevel,
    message: str,
) -> SystemLog:
    """Records an operational event or alert in logs.system_logs."""
    try:
        log_entry = SystemLog(
            service=service,
            level=level,
            message=message,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        logger.error(f"Failed to record system log entry: {e}")
        db.rollback()
        return None


def get_system_health(db: Session) -> dict:
    """
    Lightweight, honest system health monitoring (Major_Final_!.md §5.1):
    Checks Neon DB connectivity latency, external API reachability, and recent error rates.
    """
    health_details = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {"status": "unreachable", "latency_ms": None},
        "external_services": {
            "open_meteo": {"status": "unknown"},
            "gemini_ai": {"status": "missing_api_key"},
            "data_gov_in": {"status": "missing_api_key"},
        },
        "system_metrics": {
            "total_system_logs": 0,
            "errors_last_24h": 0,
        },
    }

    # 1. Database Connectivity & Roundtrip Latency
    try:
        t0 = time.perf_counter()
        db.execute(text("SELECT 1"))
        latency = round((time.perf_counter() - t0) * 1000, 2)
        health_details["database"] = {"status": "connected", "latency_ms": latency}
    except Exception as e:
        health_details["database"] = {"status": "unreachable", "error": str(e)[:100]}
        health_details["status"] = "unhealthy"

    # 2. Open-Meteo Reachability Check
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get("https://api.open-meteo.com/v1/forecast?latitude=13.9299&longitude=75.5681&current=temperature_2m")
            if resp.status_code == 200:
                health_details["external_services"]["open_meteo"] = {"status": "connected", "response_code": 200}
            else:
                health_details["external_services"]["open_meteo"] = {"status": "degraded", "response_code": resp.status_code}
    except Exception as e:
        health_details["external_services"]["open_meteo"] = {"status": "unreachable", "error": str(e)[:100]}
        if health_details["status"] == "healthy":
            health_details["status"] = "degraded"

    # 3. Gemini API Key Configuration Check
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
        health_details["external_services"]["gemini_ai"] = {"status": "configured", "model": "gemini-flash-latest"}
    else:
        health_details["external_services"]["gemini_ai"] = {"status": "unconfigured_rule_fallback_active"}

    # 4. Data.gov.in API Key Configuration Check
    if settings.DATA_GOV_IN_API_KEY and settings.DATA_GOV_IN_API_KEY.strip():
        health_details["external_services"]["data_gov_in"] = {"status": "configured", "resource_id": "35985678-0d79-46b4-9ed6-6f13308a1d24"}
    else:
        health_details["external_services"]["data_gov_in"] = {"status": "unconfigured_synthetic_active"}

    # 5. System Logs Metrics (Error Count in Last 24 Hours)
    try:
        since_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        total_logs = db.query(SystemLog).count()
        recent_errors = (
            db.query(SystemLog)
            .filter(SystemLog.level == LogLevel.ERROR, SystemLog.logged_at >= since_24h)
            .count()
        )
        health_details["system_metrics"]["total_system_logs"] = total_logs
        health_details["system_metrics"]["errors_last_24h"] = recent_errors

        if recent_errors > 20 and health_details["status"] == "healthy":
            health_details["status"] = "degraded"
    except Exception as e:
        logger.warning(f"Failed to query system log metrics: {e}")

    return health_details
