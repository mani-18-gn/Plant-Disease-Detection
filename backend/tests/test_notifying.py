import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.main import app
from backend.db.session import SessionLocal
from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm
from backend.db.models.core.crop_block import CropBlock
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority, AdvisorySource
from backend.db.models.logs.notification import Notification, NotificationChannel, NotificationStatus
from backend.db.models.logs.system_log import SystemLog, LogLevel
from backend.auth.jwt_handler import hash_password, create_access_token
from backend.agents.notifying.notifications import (
    send_notification,
    dispatch_advisory_notifications,
    get_notifications_for_farmer,
)
from backend.agents.notifying.monitoring import get_system_health, log_system_event

client = TestClient(app)


def test_notification_channels_and_dispatch_logic():
    """Verify channel status behaviors and Table 4.5 priority dispatch logic."""
    db = SessionLocal()
    try:
        # Create throwaway user/profile for testing
        u = User(username="test_notif_temp_user", phone="9990001111", password_hash=hash_password("p"), role=UserRole.FARMER)
        db.add(u)
        db.commit()

        prof = FarmerProfile(user_id=u.id, full_name="Notif Tester")
        db.add(prof)
        db.commit()

        # 1. In-App Notification: Sent immediately
        n_inapp = send_notification(db, str(prof.id), NotificationChannel.IN_APP, "Test in-app notification")
        assert n_inapp.status == NotificationStatus.SENT
        assert n_inapp.sent_at is not None

        # 2. SMS Notification: Marked pending (mock queue)
        n_sms = send_notification(db, str(prof.id), NotificationChannel.SMS, "Test SMS alert")
        assert n_sms.status == NotificationStatus.PENDING
        assert n_sms.sent_at is None

        # 3. Table 4.5 Dispatch: Urgent Advisory (Both IN_APP and SMS)
        adv_urgent = Advisory(
            farmer_id=str(prof.id),
            priority=AdvisoryPriority.URGENT,
            message="Immediate Koleroga spray needed",
            generated_by=AdvisorySource.RULE_FALLBACK,
        )
        db.add(adv_urgent)
        db.commit()

        urgent_notifs = dispatch_advisory_notifications(db, adv_urgent)
        assert len(urgent_notifs) == 2
        channels = [n.channel for n in urgent_notifs]
        assert NotificationChannel.IN_APP in channels
        assert NotificationChannel.SMS in channels

        # 4. Table 4.5 Dispatch: Medium Advisory (IN_APP only)
        adv_med = Advisory(
            farmer_id=str(prof.id),
            priority=AdvisoryPriority.MEDIUM,
            message="Check soil moisture",
            generated_by=AdvisorySource.RULE_FALLBACK,
        )
        db.add(adv_med)
        db.commit()

        med_notifs = dispatch_advisory_notifications(db, adv_med)
        assert len(med_notifs) == 1
        assert med_notifs[0].channel == NotificationChannel.IN_APP

        # 5. Table 4.5 Dispatch: Low Advisory (0 notifications)
        adv_low = Advisory(
            farmer_id=str(prof.id),
            priority=AdvisoryPriority.LOW,
            message="Routine maintenance",
            generated_by=AdvisorySource.RULE_FALLBACK,
        )
        db.add(adv_low)
        db.commit()

        low_notifs = dispatch_advisory_notifications(db, adv_low)
        assert len(low_notifs) == 0
    finally:
        u_del = db.query(User).filter(User.username == "test_notif_temp_user").first()
        if u_del:
            db.delete(u_del)
        db.commit()
        db.close()


def test_monitoring_health_and_system_event_logging():
    """Verify health check probe and system event logger."""
    db = SessionLocal()
    try:
        # 1. System Event Logging
        log_entry = log_system_event(db, service="test_service", level=LogLevel.INFO, message="Health check test event")
        assert log_entry is not None
        assert log_entry.service == "test_service"

        # 2. System Health Probe
        health = get_system_health(db)
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert health["database"]["status"] == "connected"
        assert health["database"]["latency_ms"] is not None
        assert "open_meteo" in health["external_services"]
        assert "gemini_ai" in health["external_services"]
        assert "data_gov_in" in health["external_services"]
        assert health["system_metrics"]["total_system_logs"] >= 1
    finally:
        db.close()


@pytest.fixture(scope="module")
def setup_notifying_env():
    db = SessionLocal()
    try:
        for name in ["test_notif_user_a", "test_notif_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()

        u_a = User(username="test_notif_user_a", phone="9999999991", password_hash=hash_password("p1"), role=UserRole.FARMER)
        u_b = User(username="test_notif_user_b", phone="9999999992", password_hash=hash_password("p2"), role=UserRole.FARMER)
        db.add_all([u_a, u_b])
        db.commit()

        token_a = create_access_token({"sub": str(u_a.id)})
        token_b = create_access_token({"sub": str(u_b.id)})

        h_a = {"Authorization": f"Bearer {token_a}"}
        h_b = {"Authorization": f"Bearer {token_b}"}

        prof_a = FarmerProfile(user_id=u_a.id, full_name="Notifying Tester A")
        prof_b = FarmerProfile(user_id=u_b.id, full_name="Notifying Tester B")
        db.add_all([prof_a, prof_b])
        db.commit()

        farm_a = Farm(farmer_id=prof_a.id, farm_name="Notifying Farm A", latitude=13.9299, longitude=75.5681)
        db.add(farm_a)
        db.commit()

        block_a = CropBlock(farm_id=farm_a.id, block_name="Notifying Block A", variety="Mohitnagar", planting_date="2018-01-01")
        db.add(block_a)
        db.commit()

        yield {
            "h_a": h_a,
            "h_b": h_b,
            "prof_a_id": str(prof_a.id),
            "prof_b_id": str(prof_b.id),
            "block_a_id": str(block_a.id),
        }
    finally:
        for name in ["test_notif_user_a", "test_notif_user_b"]:
            u = db.query(User).filter(User.username == name).first()
            if u:
                db.delete(u)
        db.commit()
        db.close()


def test_notifying_router_endpoints_and_e2e_dispatch(setup_notifying_env):
    h_a = setup_notifying_env["h_a"]
    h_b = setup_notifying_env["h_b"]
    prof_a_id = setup_notifying_env["prof_a_id"]
    block_a_id = setup_notifying_env["block_a_id"]

    # 1. Public Health Check Endpoint (No token required)
    res_health = client.get("/api/v1/agents/notifying/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["database"]["status"] == "connected"

    # 2. User A sends a notification to their own profile
    send_payload = {
        "farmer_id": prof_a_id,
        "channel": "in_app",
        "content": "Custom crop alert message",
    }
    res_send = client.post("/api/v1/agents/notifying/send", json=send_payload, headers=h_a)
    assert res_send.status_code == 201, res_send.text
    data_send = res_send.json()
    assert data_send["farmer_id"] == prof_a_id
    assert data_send["status"] == "sent"

    # 3. List farmer notifications
    res_list = client.get(f"/api/v1/agents/notifying/{prof_a_id}", headers=h_a)
    assert res_list.status_code == 200
    notifs = res_list.json()
    assert len(notifs) >= 1

    # 4. Cross-farmer security rejection (User B trying to send notification to User A)
    res_b = client.post("/api/v1/agents/notifying/send", json=send_payload, headers=h_b)
    assert res_b.status_code == 403, "User B should be forbidden from sending notification to User A"

    # 5. E2E Automatic Notification Triggering on Advisory Generation
    adv_payload = {"crop_block_id": block_a_id}
    res_adv = client.post("/api/v1/agents/advisory/generate", json=adv_payload, headers=h_a)
    assert res_adv.status_code == 200

    # Verify notification was automatically created in logs.notifications
    res_list_after = client.get(f"/api/v1/agents/notifying/{prof_a_id}", headers=h_a)
    assert res_list_after.status_code == 200
    notifs_after = res_list_after.json()
    assert len(notifs_after) > len(notifs), "New advisory should have triggered automatic notification creation"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
