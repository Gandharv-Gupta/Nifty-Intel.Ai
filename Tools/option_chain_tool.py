import os

from dotenv import load_dotenv
from langchain.tools import tool

from shared_qdrant import scroll_points

load_dotenv()

qdrant_collection_name_nifty_option = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_OPTION")


@tool
def get_option_chain(expiry: str, strike_price: int = None):
    """
    Fetch NIFTY option chain data for a given expiry.
    Optionally filter by strike price.
    Input:
    expiry: str = The expiry date of the option chain.
    strike_price: int = The strike price of the option chain.
    Output:
    list = The option chain data for the given expiry and strike price.
    Example:
    [
        {
            "symbol": "NIFTY",
            "expiry": "23-Jun-2026",
            "strike_price": 10000,
            "ce_oi": 10000,
            "ce_change_oi": 1000,
            "ce_volume": 10000,
            "ce_iv": 1000,
            "ce_last_price": 10000
        }
    ]
    """

    results, err = scroll_points(
        collection_name=qdrant_collection_name_nifty_option,
        limit=500,
        with_payload=True,
        with_vectors=False,
    )
    if err:
        return err

    filtered = [
        r.payload for r in results if r.payload.get("expiry") == expiry
    ]

    if strike_price:
        filtered = [
            x for x in filtered if x["strike_price"] == strike_price
        ]

    return filtered
