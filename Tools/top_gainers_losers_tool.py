import os

from dotenv import load_dotenv
from langchain.tools import tool

from shared_qdrant import scroll_collect_all

load_dotenv()

qdrant_collection_name_nifty_50 = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_50")


def _is_equity_snapshot_payload(p: dict | None) -> bool:
    if not p:
        return False
    if p.get("source") == "market_data":
        return True
    if p.get("source"):
        return False
    return bool(p.get("symbol")) and any(
        k in p for k in ("last_price", "pchange", "change", "previous_close")
    )


def _pchange_value(payload: dict | None) -> float:
    if not payload:
        return 0.0
    raw = payload.get("pchange")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


@tool
def get_top_movers(side: str = "gainers"):
    """
    Get top 5 gainers or losers based on pchange from the Nifty 50 snapshot in Qdrant.
    side: use the string 'gainers' for top positive pchange, or 'losers' for most negative pchange.
    Input:
    side: str = Either "gainers" or "losers" (default "gainers").
    Output:
    list = Up to five dicts with symbol, pchange, last_price.
    """

    results, err = scroll_collect_all(
        collection_name=qdrant_collection_name_nifty_50,
        scroll_filter=None,
        page_size=256,
        max_points=5000,
    )
    if err:
        return err

    results = [r for r in results if _is_equity_snapshot_payload(r.payload)]

    s = (side or "gainers").strip().lower()
    if s not in ("gainers", "losers"):
        s = "gainers"
    reverse = s == "gainers"

    sorted_data = sorted(results, key=lambda x: _pchange_value(x.payload), reverse=reverse)

    out: list[dict] = []
    for r in sorted_data[:5]:
        p = r.payload or {}
        sym = p.get("symbol")
        if sym is None:
            continue
        out.append(
            {
                "symbol": sym,
                "pchange": p.get("pchange"),
                "last_price": p.get("last_price"),
            }
        )
    return out
