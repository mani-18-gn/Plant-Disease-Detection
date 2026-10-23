import logging
from datetime import datetime, date, timedelta
import httpx
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.models.market.market_price import MarketPrice

logger = logging.getLogger(__name__)

DATA_GOV_RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"
DATA_GOV_BASE_URL = f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID}"


def fetch_live_market_prices(mandi_name: str = "Shivamogga", limit: int = 100) -> dict:
    """
    Fetches real arecanut market arrival prices from data.gov.in API.
    Converts Modal_Price (Rs/quintal) to price_per_kg (Rs/kg).
    If API key is missing, network times out, or rate limits occur,
    returns explicit synthetic fallback data.
    """
    api_key = settings.DATA_GOV_IN_API_KEY.strip()

    if api_key:
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": limit,
            "filters[state]": "Karnataka",
            "filters[commodity]": "Arecanut(Betelnut/Supari)",
        }
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            with httpx.Client(timeout=30.0, headers=headers) as client:
                resp = client.get(DATA_GOV_BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    records = data.get("records", [])

                    matched_prices = []
                    # Filter for target mandi or general Karnataka arecanut records
                    for r in records:
                        market = r.get("Market", "")
                        if not mandi_name or mandi_name.lower() in market.lower() or "shivamogga" in market.lower() or "shimoga" in market.lower() or "sagar" in market.lower():
                            modal_val = r.get("Modal_Price")
                            if modal_val is not None:
                                try:
                                    price_kg = float(modal_val) / 100.0  # Convert quintal to kg
                                    arr_date_str = r.get("Arrival_Date", "")
                                    p_date = datetime.strptime(arr_date_str, "%d/%m/%Y").date() if arr_date_str else date.today()

                                    matched_prices.append({
                                        "mandi_name": market or mandi_name,
                                        "commodity": "Arecanut",
                                        "variety": r.get("Variety", "Rashi"),
                                        "price_per_kg": round(price_kg, 2),
                                        "price_date": p_date,
                                        "source": "data_gov_in",
                                    })
                                except Exception as parse_err:
                                    logger.warning(f"Error parsing data.gov.in record: {parse_err}")

                    if matched_prices:
                        logger.info(f"Fetched {len(matched_prices)} real arecanut price records from data.gov.in")
                        return {
                            "prices": matched_prices,
                            "source": "data_gov_in",
                            "is_synthetic": False,
                        }
                else:
                    logger.warning(f"data.gov.in API returned status {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"data.gov.in API connection error: {e}")

    # Fallback to realistic synthetic current prices for Karnataka APMC
    logger.warning("Using synthetic_fallback market prices for Karnataka APMC.")
    today = date.today()
    synthetic_prices = [
        {"mandi_name": mandi_name or "Shivamogga APMC", "commodity": "Arecanut", "variety": "Rashi", "price_per_kg": 475.50, "price_date": today, "source": "synthetic_fallback", "description": "Red whole boiled arecanut (Premium)"},
        {"mandi_name": mandi_name or "Shivamogga APMC", "commodity": "Arecanut", "variety": "Bette", "price_per_kg": 566.09, "price_date": today, "source": "synthetic_fallback", "description": "Half-cut boiled arecanut (Standard)"},
        {"mandi_name": mandi_name or "Shivamogga APMC", "commodity": "Arecanut", "variety": "Chali", "price_per_kg": 380.00, "price_date": today, "source": "synthetic_fallback", "description": "Sun-dried ripe white arecanut"},
        {"mandi_name": mandi_name or "Shivamogga APMC", "commodity": "Arecanut", "variety": "Gorabal", "price_per_kg": 420.00, "price_date": today, "source": "synthetic_fallback", "description": "Unboiled dried whole arecanut"},
        {"mandi_name": mandi_name or "Shivamogga APMC", "commodity": "Arecanut", "variety": "Api", "price_per_kg": 540.00, "price_date": today, "source": "synthetic_fallback", "description": "Tender green boiled arecanut"},
    ]
    return {
        "prices": synthetic_prices,
        "source": "synthetic_fallback",
        "is_synthetic": True,
    }


def sync_market_prices(db: Session, mandi_name: str = "Shivamogga") -> list[MarketPrice]:
    """
    Syncs live prices from data.gov.in into the market.market_prices database table.
    Avoids duplicate entries for the same mandi and date.
    """
    fetch_res = fetch_live_market_prices(mandi_name=mandi_name)
    prices_data = fetch_res["prices"]

    saved_records = []
    for item in prices_data:
        existing = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.mandi_name == item["mandi_name"],
                MarketPrice.commodity == item["commodity"],
                MarketPrice.price_date == item["price_date"],
            )
            .first()
        )
        if not existing:
            new_price = MarketPrice(
                mandi_name=item["mandi_name"],
                commodity=item["commodity"],
                price_per_kg=item["price_per_kg"],
                price_date=item["price_date"],
                source=item["source"],
            )
            db.add(new_price)
            saved_records.append(new_price)

    if saved_records:
        db.commit()
        for r in saved_records:
            db.refresh(r)

    return saved_records
