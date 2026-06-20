from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain.tools import tool
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

from shared_qdrant import scroll_collect_all, scroll_points

load_dotenv()

qdrant_collection_name_nifty_50 = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_50")


def _is_equity_snapshot_payload(p: dict | None) -> bool:
    """Keep Nifty 50 cash rows; avoid relying on Qdrant filter for unindexed `source` field."""
    if not p:
        return False
    if p.get("source") == "market_data":
        return True
    if p.get("source"):
        return False
    return bool(p.get("symbol")) and any(
        k in p for k in ("last_price", "pchange", "change", "previous_close")
    )


def _payload_symbol_matches(requested: str, payload_symbol: str | None) -> bool:
    """Match NSE-style symbols; NIFTY index row is often NIFTY 50, not NIFTY."""
    if not requested or payload_symbol is None:
        return False
    req = requested.upper().strip()
    ps = str(payload_symbol).upper().strip()
    if ps == req:
        return True
    req_ns = req.replace(" ", "")
    ps_ns = ps.replace(" ", "")
    if req_ns == ps_ns:
        return True
    if req_ns == "NIFTY" and ps_ns in ("NIFTY50", "NIFTY"):
        return True
    return False


def _nifty_index_filter() -> Filter:
    """Uses indexed `symbol` only (no `source` filter — that field may lack a payload index)."""
    return Filter(
        must=[
            FieldCondition(
                key="symbol",
                match=MatchAny(any=["NIFTY", "NIFTY 50", "NIFTY50"]),
            ),
        ]
    )


def _exact_symbol_filter(sym: str) -> Filter:
    return Filter(must=[FieldCondition(key="symbol", match=MatchValue(value=sym))])


def _collect_market_rows() -> tuple[list[Any], str | None]:
    """Scroll entire collection without server-side filter on unindexed fields."""
    rows, err = scroll_collect_all(
        collection_name=qdrant_collection_name_nifty_50,
        scroll_filter=None,
        page_size=256,
        max_points=5000,
    )
    if err:
        return [], err
    return [r for r in rows if _is_equity_snapshot_payload(r.payload)], None


@tool
def get_market_data(symbol: str = None):
    """
    Fetch Nifty 50 market data from Qdrant.
    If symbol is provided, returns that stock's payload (exact NSE ticker, e.g. INFY, TCS).
    If symbol is omitted, returns all ingested market_data rows (paginated internally).
    For the index row use NIFTY (aliases NIFTY 50 / NIFTY50 in storage).
    """

    if not qdrant_collection_name_nifty_50:
        return "Collection name is missing (check QDRANT_COLLECTION_NAME_NIFTY_50 in .env)."

    if symbol:
        sym = str(symbol).strip().upper()
        if not sym:
            sym = ""

        if sym in ("NIFTY", "NIFTY50", "NIFTY 50"):
            rows, err = scroll_points(
                collection_name=qdrant_collection_name_nifty_50,
                limit=20,
                scroll_filter=_nifty_index_filter(),
            )
            if err:
                return err
            candidates = [r for r in rows if _is_equity_snapshot_payload(r.payload)]
            if candidates:
                return candidates[0].payload
            all_rows, err2 = _collect_market_rows()
            if err2:
                return err2
            for r in all_rows:
                if _payload_symbol_matches("NIFTY", (r.payload or {}).get("symbol")):
                    return r.payload
            return "Symbol not found"

        rows, err = scroll_points(
            collection_name=qdrant_collection_name_nifty_50,
            limit=20,
            scroll_filter=_exact_symbol_filter(sym),
        )
        if err:
            return err
        candidates = [r for r in rows if _is_equity_snapshot_payload(r.payload)]
        if candidates:
            return candidates[0].payload

        all_rows, err2 = _collect_market_rows()
        if err2:
            return err2
        for r in all_rows:
            if _payload_symbol_matches(sym, (r.payload or {}).get("symbol")):
                return r.payload
        return "Symbol not found"

    all_rows, err = _collect_market_rows()
    if err:
        return err
    return [r.payload for r in all_rows]
