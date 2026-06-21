import os
import sys
import tempfile

import fitz  # pymupdf
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from qdrant_client import QdrantClient

load_dotenv()

_NSE_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive",
}


def _fetch_pdf_bytes(pdf_url: str, timeout: int = 60) -> tuple[bytes | None, str]:
    """NSE PDFs need cookies + browser-like headers."""
    base = (os.getenv("NSE_BASE_URL") or "https://www.nseindia.com").rstrip("/")
    session = requests.Session()
    session.headers.update(_NSE_BROWSER_HEADERS)
    try:
        session.get(f"{base}/", timeout=min(15, timeout))
        response = session.get(pdf_url, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        return None, f"network error: {exc}"
    if response.status_code != 200:
        return None, f"HTTP {response.status_code}"
    data = response.content
    if len(data) < 5 or not data.lstrip().startswith(b"%PDF"):
        return None, "not a PDF (blocked, login page, or empty body)"
    return data, ""


client = QdrantClient(
    url=os.getenv("QDRANT_CLUSTER_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


@tool
def get_company_documents_tool(symbol: str):
    """Fetch company announcement records from Qdrant (e.g. INFY, TCS, RELIANCE)."""
    coll = os.getenv("QDRANT_COLLECTION_NAME_COMPANY_DOCUMENTS")
    results, _ = client.scroll(
        collection_name=coll,
        limit=100,
        with_payload=True,
        with_vectors=False,
    )
    sym = symbol.upper()
    return [p.payload for p in results if p.payload.get("symbol") == sym]


@tool
def extract_pdf_text_tool(pdf_url: str):
    """Download a PDF and extract text (truncated for context limits)."""
    raw, err = _fetch_pdf_bytes(pdf_url)
    if raw is None:
        return f"Unable to download PDF ({err})"

    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
        temp_pdf.write(raw)
        temp_pdf.flush()
        doc = fitz.open(temp_pdf.name)
        try:
            text = "".join(page.get_text() for page in doc)
        finally:
            doc.close()
        return text[:20000]




if __name__ == "__main__":
    rows = get_company_documents_tool.invoke({"symbol":"DMART"})
    print(rows)
    pdf_url = rows[0].get("pdf_url") if rows else None
    if not pdf_url:
        print("No PDF URL found")
        exit(1)
    text = extract_pdf_text_tool.invoke({"pdf_url": pdf_url})
    body = text if isinstance(text, str) else str(text)
    print(body[:1200] + ("…" if len(body) > 1200 else ""))

