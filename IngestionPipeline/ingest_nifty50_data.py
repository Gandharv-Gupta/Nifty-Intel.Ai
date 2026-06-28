import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from qdrant_client.models import PointStruct

from shared_qdrant import client
from .embedding_model import embed_text

qdrant_collection_name_nifty_50 = os.getenv(
    "QDRANT_COLLECTION_NAME_NIFTY_50"
)

def build_market_text(stock: dict) -> str:
    return f"""
    Symbol: {stock.get('symbol')}
    Last Price: {stock.get('lastPrice')}
    Change: {stock.get('change')}
    Percentage Change: {stock.get('pChange')}
    Open: {stock.get('open')}
    Day High: {stock.get('dayHigh')}
    Day Low: {stock.get('dayLow')}
    Previous Close: {stock.get('previousClose')}
    Volume: {stock.get('totalTradedVolume')}
    Traded Value: {stock.get('totalTradedValue')}
    52 Week High: {stock.get('yearHigh')}
    52 Week Low: {stock.get('yearLow')}
    Last Update Time: {stock.get('lastUpdateTime')}
    """.strip()


def store_market_data(data: dict):

    market_records = data.get("data", [])
    if not market_records:
        print("[Nifty50][Store] No records found; skipping upsert")
        return

    print(f"[Nifty50][Store] Preparing {len(market_records)} records")



    market_date = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d")

    points = []

    for stock in market_records:
        print("[Nifty50][Store] Building stock data")

        text = build_market_text(stock)
        
        print("[Nifty50][Store] Creating embedding")

        vector = embed_text(text)

        print("[Nifty50][Store] Preparing payload for Qdrant upsert")

        payload = {
            "source": "market_data",
            "market_date": market_date,

            "symbol": stock.get("symbol"),

            "last_price": stock.get("lastPrice"),
            "change": stock.get("change"),
            "pchange": stock.get("pChange"),

            "volume": stock.get("totalTradedVolume"),
            "traded_value": stock.get("totalTradedValue"),

            "open": stock.get("open"),
            "day_high": stock.get("dayHigh"),
            "day_low": stock.get("dayLow"),

            "previous_close": stock.get("previousClose"),

            "year_high": stock.get("yearHigh"),
            "year_low": stock.get("yearLow"),

            "last_update_time": stock.get("lastUpdateTime"),

            "ingested_at": datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).isoformat(),

            "raw_record": stock
        }

        print("[Nifty50][Store] Creating PointStruct")
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
        )

    print("[Nifty50][Store] Upserting data")
    client.upsert(
        collection_name=qdrant_collection_name_nifty_50,
        points=points
    )

    print(
        f"[Nifty50][Store] Upserted {len(points)} records to "
        f"'{qdrant_collection_name_nifty_50}'"
    )