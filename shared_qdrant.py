"""
Single Qdrant client for ingestion and agent tools.

Same construction pattern as IngestionPipeline/ingest_nifty50_data.py
and ingest_nifty_option_data.py so env and connectivity behave consistently.
"""

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Filter

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLUSTER_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

# Default client REST timeout is very short; cloud scrolls often exceed it and tools then fail.
client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    check_compatibility=False,
    timeout=120,
)


def format_qdrant_exception(exc: BaseException) -> str:
    text = str(exc).lower()
    if "nodename nor servname" in text or "errno 8" in text:
        return (
            "Could not resolve Qdrant host (DNS error). Check QDRANT_CLUSTER_URL in .env "
            "matches Qdrant Cloud (include https://), then retry."
        )
    return f"Qdrant error: {exc!s}"


def _is_transient_network(exc: BaseException) -> bool:
    """DNS blips and short-lived TCP issues — worth longer backoff between retries."""
    t = str(exc).lower()
    return any(
        frag in t
        for frag in (
            "nodename nor servname",
            "errno 8",
            "gaierror",
            "name or service not known",
            "temporary failure in name resolution",
            "connection reset",
            "connection aborted",
            "timed out",
            "timeout",
            "temporarily unavailable",
        )
    )


def _sleep_before_scroll_retry(attempt: int, exc: BaseException) -> None:
    if attempt >= 2:
        return
    if _is_transient_network(exc):
        time.sleep(1.0 * (2**attempt))
    else:
        time.sleep(0.35 * (attempt + 1))


def _scroll_attempt(
    *,
    collection_name: str,
    limit: int,
    scroll_filter: Filter | None,
    offset: Any,
    with_payload: bool,
    with_vectors: bool,
) -> tuple[list[Any], Any]:
    return client.scroll(
        collection_name=collection_name,
        scroll_filter=scroll_filter,
        limit=limit,
        offset=offset,
        with_payload=with_payload,
        with_vectors=with_vectors,
    )


def scroll_points(
    *,
    collection_name: str | None,
    limit: int,
    with_payload: bool = True,
    with_vectors: bool = False,
    scroll_filter: Filter | None = None,
    offset: Any = None,
):
    """
    Scroll using the shared client. Returns (points, error_message).
    On error, points is [] and error_message is user-facing text for the agent.

    Note: Without scroll_filter, Qdrant returns an arbitrary slice of up to `limit`
    points (by internal order). For symbol-specific or full-universe reads, use a
    payload filter or scroll_collect_all.
    """
    if not collection_name:
        return [], "Collection name is missing (check QDRANT_COLLECTION_* env vars)."

    last_exc: BaseException | None = None
    for attempt in range(3):
        try:
            points, _next = _scroll_attempt(
                collection_name=collection_name,
                limit=limit,
                scroll_filter=scroll_filter,
                offset=offset,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            return points, None
        except (ResponseHandlingException, OSError, TimeoutError) as exc:
            last_exc = exc
        except Exception as exc:
            last_exc = exc
        if attempt < 2:
            _sleep_before_scroll_retry(attempt, last_exc or RuntimeError("unknown"))

    return [], format_qdrant_exception(last_exc or RuntimeError("unknown scroll failure"))


def scroll_collect_all(
    *,
    collection_name: str | None,
    scroll_filter: Filter | None = None,
    page_size: int = 256,
    max_points: int = 5000,
    with_payload: bool = True,
    with_vectors: bool = False,
):
    """
    Page through Qdrant until no next offset or max_points reached.
    Returns (all_points, error_message).
    """
    if not collection_name:
        return [], "Collection name is missing (check QDRANT_COLLECTION_* env vars)."

    acc: list[Any] = []
    next_offset: Any = None
    last_exc: BaseException | None = None

    while len(acc) < max_points:
        lim = min(page_size, max_points - len(acc))
        for attempt in range(3):
            try:
                batch, next_offset = _scroll_attempt(
                    collection_name=collection_name,
                    limit=lim,
                    scroll_filter=scroll_filter,
                    offset=next_offset,
                    with_payload=with_payload,
                    with_vectors=with_vectors,
                )
                acc.extend(batch)
                last_exc = None
                break
            except (ResponseHandlingException, OSError, TimeoutError) as exc:
                last_exc = exc
            except Exception as exc:
                last_exc = exc
            if attempt < 2:
                _sleep_before_scroll_retry(attempt, last_exc or RuntimeError("unknown"))
        else:
            return [], format_qdrant_exception(last_exc or RuntimeError("scroll page failed"))

        if next_offset is None:
            break

    return acc, None
