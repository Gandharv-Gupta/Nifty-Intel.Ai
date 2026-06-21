import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from shared_qdrant import client

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

qdrant_collection_name_nifty_option = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_OPTION")


def build_option_text(record: dict) -> str:

    ce = record.get("CE", {})
    pe = record.get("PE", {})

    return f"""
    Underlying: NIFTY

    Expiry: {record.get("expiryDates")}
    Strike Price: {record.get("strikePrice")}

    Call Option:
    Open Interest: {ce.get("openInterest")}
    Change in Open Interest: {ce.get("changeinOpenInterest")}
    Volume: {ce.get("totalTradedVolume")}
    Implied Volatility: {ce.get("impliedVolatility")}
    Last Price: {ce.get("lastPrice")}

    Put Option:
    Open Interest: {pe.get("openInterest")}
    Change in Open Interest: {pe.get("changeinOpenInterest")}
    Volume: {pe.get("totalTradedVolume")}
    Implied Volatility: {pe.get("impliedVolatility")}
    Last Price: {pe.get("lastPrice")}
    """.strip()


def store_option_chain_data(data: dict):

    option_records = data["records"]["data"]

    points = []

    for record in option_records:

        ce = record.get("CE", {})
        pe = record.get("PE", {})

        text = build_option_text(record)

        vector = embedding_model.encode(text).tolist()

        payload = {

            # metadata
            "source": "option_chain",
            "symbol": "NIFTY",

            "expiry": record.get("expiryDates"),
            "strike_price": record.get("strikePrice"),

            # CE
            "ce_oi": ce.get("openInterest"),
            "ce_change_oi": ce.get("changeinOpenInterest"),
            "ce_volume": ce.get("totalTradedVolume"),
            "ce_iv": ce.get("impliedVolatility"),
            "ce_last_price": ce.get("lastPrice"),

            # PE
            "pe_oi": pe.get("openInterest"),
            "pe_change_oi": pe.get("changeinOpenInterest"),
            "pe_volume": pe.get("totalTradedVolume"),
            "pe_iv": pe.get("impliedVolatility"),
            "pe_last_price": pe.get("lastPrice"),

            # useful for auditing
            "ingested_at": datetime.now().isoformat(),

            # optional raw data
            "raw_record": record
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
        )

    client.upsert(
        collection_name=qdrant_collection_name_nifty_option,
        points=points
    )

    print(
        f"Stored {len(points)} option-chain records in '{qdrant_collection_name_nifty_option}'"
    )