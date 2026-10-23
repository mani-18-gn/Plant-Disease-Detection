import os
import sys
from datetime import date, datetime, timedelta

# Ensure python path finds root packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.db.session import SessionLocal
import backend.db.models  # ensure models registered

from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.core.farm import Farm, IrrigationType
from backend.db.models.core.crop_block import CropBlock, BlockStatus
from backend.db.models.core.iot_device import IoTDevice
from backend.db.models.agronomy.farm_activity import FarmActivity, ActivityType, LoggedVia
from backend.db.models.agronomy.disease_detection import DiseaseDetection
from backend.db.models.env.weather_reading import WeatherReading, WeatherSource
from backend.db.models.env.soil_sensor_reading import SoilSensorReading
from backend.db.models.market.market_price import MarketPrice
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority, AdvisorySource
from backend.db.models.logs.feedback import Feedback
from backend.db.models.logs.notification import Notification, NotificationChannel, NotificationStatus
from backend.auth.jwt_handler import hash_password


def seed():
    print("[...] Connecting to database session...")
    db = SessionLocal()
    try:
        # Idempotency check & clean up existing seed data if present
        existing_user = db.query(User).filter(User.username == "farmer_demo").first()
        if existing_user:
            print("[INFO] Cleaning up existing 'farmer_demo' seed data for clean re-seed...")
            db.delete(existing_user)
            db.flush()

        # Clean up market prices seeded by previous run
        db.query(MarketPrice).filter(MarketPrice.mandi_name == "Shivamogga APMC").delete()
        db.flush()

        print("[...] Inserting complete 13-table end-to-end sample data chain...")

        # 1. core.users
        user = User(
            username="farmer_demo",
            phone="9876543210",
            password_hash=hash_password("password123"),
            role=UserRole.FARMER,
        )
        db.add(user)
        db.flush()

        # 2. core.farmer_profiles
        profile = FarmerProfile(
            user_id=user.id,
            full_name="Ramesh Gowda",
            village="Thirthahalli",
            taluk="Thirthahalli",
            district="Shivamogga",
            state="Karnataka",
            pincode="577432",
            preferred_language="kn",
            preferred_mandi="Shivamogga APMC",
        )
        db.add(profile)
        db.flush()

        # 3. core.farms
        farm = Farm(
            farmer_id=profile.id,
            farm_name="Green Plantation Plot #1",
            latitude=13.6961,
            longitude=75.2427,
            total_area_acres=4.5,
            soil_type="Red Laterite",
            irrigation_type=IrrigationType.DRIP,
        )
        db.add(farm)
        db.flush()

        # 4. core.crop_blocks (perennial block, planted 6 years ago)
        crop_block = CropBlock(
            farm_id=farm.id,
            block_name="Block A – 2018 Mature Batch",
            variety="Mangala",
            planting_date=date.today() - timedelta(days=365 * 6),
            number_of_trees=450,
            spacing_meters=2.7,
            status=BlockStatus.ACTIVE,
            notes="High-yielding mature block with installed drip irrigation lines.",
        )
        db.add(crop_block)
        db.flush()

        # 5. core.iot_devices
        device = IoTDevice(
            farm_id=farm.id,
            device_token="esp32_soil_sensor_01",
            device_type="soil_moisture_v1",
        )
        db.add(device)
        db.flush()

        # 6. agronomy.farm_activities (3-4 rows linked to crop_block)
        today = date.today()
        act1 = FarmActivity(
            crop_block_id=crop_block.id,
            activity_type=ActivityType.FERTILIZER,
            activity_date=today - timedelta(days=60),
            product_used="NPK 15:15:15 + Neem Cake",
            quantity=150.0,
            quantity_unit="kg",
            cost=2800.0,
            performed_by="Self",
            details={"NPK_ratio": "15:15:15", "neem_cake_kg": 50},
            logged_via=LoggedVia.APP,
        )
        act2 = FarmActivity(
            crop_block_id=crop_block.id,
            activity_type=ActivityType.SPRAYING,
            activity_date=today - timedelta(days=10),
            product_used="Bordeaux Mixture 1%",
            quantity=20.0,
            quantity_unit="litre",
            cost=850.0,
            performed_by="Hired Labor",
            details={"target_disease": "Koleroga Fruit Rot"},
            logged_via=LoggedVia.APP,
        )
        act3 = FarmActivity(
            crop_block_id=crop_block.id,
            activity_type=ActivityType.IRRIGATION,
            activity_date=today - timedelta(days=2),
            quantity=2.5,
            quantity_unit="hours",
            cost=120.0,
            performed_by="Self",
            details={"method": "drip"},
            logged_via=LoggedVia.AUTO,
        )
        act4 = FarmActivity(
            crop_block_id=crop_block.id,
            activity_type=ActivityType.PRUNING,
            activity_date=today - timedelta(days=35),
            quantity=1.0,
            quantity_unit="block",
            cost=500.0,
            performed_by="Hired Labor",
            details={"notes": "Removed dry fronds and infected nuts"},
            logged_via=LoggedVia.APP,
        )
        db.add_all([act1, act2, act3, act4])

        # 7. agronomy.disease_detections
        detection = DiseaseDetection(
            crop_block_id=crop_block.id,
            image_path="/uploads/images/block_a_leaf_01.jpg",
            predicted_disease="Yellow Leaf Disease",
            cnn_confidence=0.91,
            posterior_probability=0.84,
            validated=True,
        )
        db.add(detection)

        # 8. env.weather_readings
        now_dt = datetime.now()
        weather1 = WeatherReading(
            farm_id=farm.id,
            region_key="SHIMOGA_GRID_01",
            temperature=27.5,
            humidity=86.0,
            rainfall_mm=18.5,
            source=WeatherSource.API,
            recorded_at=now_dt - timedelta(hours=6),
        )
        weather2 = WeatherReading(
            farm_id=farm.id,
            region_key="SHIMOGA_GRID_01",
            temperature=28.2,
            humidity=82.0,
            rainfall_mm=4.0,
            source=WeatherSource.API,
            recorded_at=now_dt - timedelta(hours=1),
        )
        db.add_all([weather1, weather2])

        # 9. env.soil_sensor_readings
        soil1 = SoilSensorReading(
            device_id=device.id,
            moisture_pct=42.5,
            recorded_at=now_dt - timedelta(hours=4),
        )
        soil2 = SoilSensorReading(
            device_id=device.id,
            moisture_pct=39.0,
            recorded_at=now_dt - timedelta(hours=1),
        )
        db.add_all([soil1, soil2])

        # 10. market.market_prices
        mp1 = MarketPrice(
            mandi_name="Shivamogga APMC",
            commodity="arecanut_chali",
            price_per_kg=480.0,
            price_date=today - timedelta(days=2),
            source="data.gov.in",
        )
        mp2 = MarketPrice(
            mandi_name="Shivamogga APMC",
            commodity="arecanut_chali",
            price_per_kg=485.0,
            price_date=today - timedelta(days=1),
            source="data.gov.in",
        )
        mp3 = MarketPrice(
            mandi_name="Shivamogga APMC",
            commodity="arecanut_chali",
            price_per_kg=490.0,
            price_date=today,
            source="data.gov.in",
        )
        db.add_all([mp1, mp2, mp3])
        db.flush()

        # 11. logs.advisories
        advisory = Advisory(
            farmer_id=profile.id,
            crop_block_id=crop_block.id,
            priority=AdvisoryPriority.HIGH,
            message="High humidity and recent rainfall detected in Thirthahalli region. Apply 1% Bordeaux mixture spray on Block A to prevent Koleroga (Fruit Rot) disease outbreak.",
            generated_by=AdvisorySource.RULE_FALLBACK,
            input_snapshot={
                "disease": "Koleroga Fruit Rot",
                "humidity_pct": 86.0,
                "recent_rainfall_mm": 18.5,
                "last_spray_days_ago": 10,
            },
            read_status=False,
        )
        db.add(advisory)
        db.flush()

        # 12. logs.feedback (with extra crop_block_id FK)
        fb = Feedback(
            advisory_id=advisory.id,
            farmer_id=profile.id,
            crop_block_id=crop_block.id,
            rating=4,
            outcome_notes="Applied Bordeaux mixture as advised. Fruit rot spread was prevented successfully.",
        )
        db.add(fb)

        # 13. logs.notifications
        notif = Notification(
            farmer_id=profile.id,
            channel=NotificationChannel.SMS,
            content="[ArecaAgent Alert] High Priority Advisory: Apply Bordeaux mixture spray on Block A to protect against Koleroga.",
            status=NotificationStatus.SENT,
            sent_at=now_dt,
        )
        db.add(notif)

        # Commit transaction end-to-end
        db.commit()
        print("[OK]   Successfully seeded sample data chain across all 13 tables!")
        print(f"       User login: username='farmer_demo', password='password123'")

    except Exception as e:
        db.rollback()
        print(f"[FAIL] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
