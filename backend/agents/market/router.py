import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.market.market_price import MarketPrice
from backend.auth.jwt_handler import get_current_user_optional
from backend.schemas.market import MarketAgentResponse, MarketPriceResponse, VarietyPriceItem, MarketForecastItem
from backend.agents.market.data_gov_client import fetch_live_market_prices, sync_market_prices
from backend.agents.market.lstm_model import generate_lstm_forecast, load_market_lstm, LSTM_MIN_DATA_THRESHOLD
from backend.agents.market.fallback_model import generate_fallback_price_forecast

router = APIRouter(prefix="/agents/market", tags=["Market Agent"])


@router.get("/prices", response_model=MarketAgentResponse)
def get_market_prices(
    mandi: str | None = Query(None, description="Target Mandi APMC name (e.g., Shivamogga, Sagar)"),
    mandi_name: str | None = Query(None, description="Alias for mandi"),
    commodity: str = Query("Arecanut", description="Commodity name"),
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Market Agent: Fetches current Mandi price, historical arrivals, multi-variety prices, and 7-day forecast.
    - If historical data >= 67 days, runs the 2-layer LSTM model (forecast_model='lstm').
    - If historical data < 67 days, runs linear trend regression fallback (forecast_model='linear_trend_regression').
    """
    # 1. Determine effective mandi name (accept either 'mandi' or 'mandi_name')
    effective_mandi = mandi or mandi_name
    if not effective_mandi and current_user:
        profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
        if profile and profile.preferred_mandi:
            effective_mandi = profile.preferred_mandi

    if not effective_mandi:
        effective_mandi = "Shivamogga APMC"

    # 2. Check cached prices in market.market_prices
    cached_records = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.mandi_name.ilike(f"%{effective_mandi.split()[0]}%"),
            MarketPrice.commodity.ilike(f"%{commodity}%"),
        )
        .order_by(MarketPrice.price_date.desc())
        .all()
    )

    is_synthetic = False
    source_str = "data_gov_in"

    # If few or no records exist in DB for this mandi, sync from data.gov.in
    if len(cached_records) < 3:
        sync_market_prices(db, mandi_name=effective_mandi)
        cached_records = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.mandi_name.ilike(f"%{effective_mandi.split()[0]}%"),
                MarketPrice.commodity.ilike(f"%{commodity}%"),
            )
            .order_by(MarketPrice.price_date.desc())
            .all()
        )

    # 3. Determine current price and latest date
    if cached_records:
        latest_record = cached_records[0]
        current_price = float(latest_record.price_per_kg)
        latest_date = latest_record.price_date
        source_str = latest_record.source
        is_synthetic = (source_str == "synthetic_fallback")
    else:
        # Live fallback fetch
        live_res = fetch_live_market_prices(mandi_name=effective_mandi)
        prices_list = live_res["prices"]
        latest_record_dict = prices_list[0]
        current_price = float(latest_record_dict["price_per_kg"])
        latest_date = latest_record_dict["price_date"]
        source_str = live_res["source"]
        is_synthetic = live_res["is_synthetic"]

    # 4. Extract chronological historical price series for forecasting
    historical_asc = sorted(cached_records, key=lambda r: r.price_date)
    historical_price_floats = [float(r.price_per_kg) for r in historical_asc]

    # 5. Generate 7-day Price Forecast (LSTM vs Fallback)
    lstm_weights = load_market_lstm()
    if len(historical_price_floats) >= LSTM_MIN_DATA_THRESHOLD and lstm_weights is not None:
        forecast_items = generate_lstm_forecast(
            historical_prices=historical_price_floats,
            start_date=latest_date,
            periods=7,
        )
    else:
        forecast_items = generate_fallback_price_forecast(
            historical_prices=historical_price_floats,
            current_price=current_price,
            start_date=latest_date,
            periods=7,
        )

    # 6. Extract variety prices breakdown
    live_varieties_res = fetch_live_market_prices(mandi_name=effective_mandi)
    variety_items = []
    seen_varieties = set()
    for v in live_varieties_res.get("prices", []):
        v_name = v.get("variety", "Rashi")
        if v_name not in seen_varieties:
            seen_varieties.add(v_name)
            variety_items.append(
                VarietyPriceItem(
                    variety=v_name,
                    price_per_kg=float(v["price_per_kg"]),
                    price_date=v["price_date"],
                    source=v["source"],
                    description=v.get("description", f"{v_name} arecanut grade"),
                )
            )

    # Format historical records for response (latest 20)
    pydantic_history = [
        MarketPriceResponse(
            id=uuid.UUID(str(r.id)),
            mandi_name=r.mandi_name,
            commodity=r.commodity,
            price_per_kg=float(r.price_per_kg),
            price_date=r.price_date,
            source=r.source,
        )
        for r in cached_records[:20]
    ]

    return MarketAgentResponse(
        mandi_name=effective_mandi,
        commodity=commodity,
        current_price_per_kg=round(current_price, 2),
        price_date=latest_date,
        source=source_str,
        is_synthetic=is_synthetic,
        variety_prices=variety_items,
        forecast=[MarketForecastItem(**item) if isinstance(item, dict) else item for item in forecast_items],
        historical_prices=pydantic_history,
    )
