import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from langchain.tools import tool
from qdrant_client.models import FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer

from shared_qdrant import client
from utils import load_repo_dotenv

load_repo_dotenv()

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedding_model: SentenceTransformer | None = None


def _embed_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBED_MODEL_NAME)
    return _embedding_model


def _symbol_filter(sym: str) -> Filter:
    return Filter(must=[FieldCondition(key="symbol", match=MatchValue(value=sym.upper()))])


def _top_k() -> int:
    raw = os.getenv("GET_COMPANY_DOCS_TOP_K", "5")
    try:
        k = int(str(raw).strip())
        return max(1, min(k, 20))
    except ValueError:
        return 5


@tool
def get_company_documents_tool(symbol: str, query: str = ""):
    """
    Company announcements in Qdrant (vectors include PDF + metadata from ingestion).

    - Always pass NSE `symbol` (e.g. DMART, INFY).
    - Pass the user's question or keywords as `query` to rank the best-matching points for that
      symbol (semantic search). Use the same wording the user cares about (e.g. "AGM notice",
      "dividend", "board meeting").
    - If `query` is empty, returns up to 100 rows for that symbol (scroll, no ranking).
    """
    coll = os.getenv("QDRANT_COLLECTION_NAME_COMPANY_DOCUMENTS")
    if not coll:
        return "Collection name is missing (QDRANT_COLLECTION_NAME_COMPANY_DOCUMENTS)."

    sym = symbol.upper().strip()
    if not sym:
        return "symbol is required."

    q = (query or "").strip()
    if q:
        vec = _embed_model().encode(q).tolist()
        resp = client.query_points(
            collection_name=coll,
            query=vec,
            query_filter=_symbol_filter(sym),
            limit=_top_k(),
            with_payload=True,
            with_vectors=False,
        )
        out: list[dict] = []
        for h in resp.points:
            row = dict(h.payload or {})
            row["_match_score"] = float(h.score)
            out.append(row)
        return out

    rows, _ = client.scroll(
        collection_name=coll,
        scroll_filter=_symbol_filter(sym),
        limit=100,
        with_payload=True,
        with_vectors=False,
    )
    return [p.payload for p in rows if p.payload]


if __name__ == "__main__":
    rows = get_company_documents_tool.invoke(
        {"symbol": "DMART", "query": "annual general meeting dividend"}
    )
    pdf_extracted_text = rows[0].get("pdf_extracted_text")
    print(pdf_extracted_text)
