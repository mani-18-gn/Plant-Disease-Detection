import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.db.models.logs.notification import NotificationChannel, NotificationStatus


class NotificationSendRequest(BaseModel):
    farmer_id: uuid.UUID
    channel: NotificationChannel = NotificationChannel.IN_APP
    content: str


class NotificationResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    channel: NotificationChannel
    content: str
    status: NotificationStatus
    sent_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseHealth(BaseModel):
    status: str
    latency_ms: float | None = None


class ExternalServiceHealth(BaseModel):
    open_meteo: dict
    gemini_ai: dict
    data_gov_in: dict


class SystemMetricsHealth(BaseModel):
    total_system_logs: int
    errors_last_24h: int


class HealthCheckResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    timestamp: str
    database: DatabaseHealth
    external_services: ExternalServiceHealth
    system_metrics: SystemMetricsHealth
