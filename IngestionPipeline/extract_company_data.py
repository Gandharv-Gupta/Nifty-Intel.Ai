import json
import os
import sys
import tempfile
from pathlib import Path

import fitz  # pymupdf
import requests

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from utils import load_repo_dotenv

load_repo_dotenv()

nse_base_url = os.getenv("NSE_BASE_URL")
company_announcements_url = os.getenv("NSE_COMPANY_ANNOUNCEMENTS_URL")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

# Filled by _ensure_announcements_loaded(); import-safe (no network at import time).
response: requests.Response | None = None
_session: requests.Session | None = None


def _ensure_announcements_loaded() -> None:
    """One-shot fetch of the announcements list (NSE cookies + JSON)."""
    global response, _session
    if response is not None:
        return
    _session = requests.Session()
    _session.get(nse_base_url, headers=headers, timeout=10)
    response = _session.get(
        company_announcements_url,
        headers=headers,
        timeout=10,
    )


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
        r = session.get(pdf_url, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        return None, f"network error: {exc}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    data = r.content
    if len(data) < 5 or not data.lstrip().startswith(b"%PDF"):
        return None, "not a PDF (blocked, login page, or empty body)"
    return data, ""


def extract_pdf_text(pdf_url: str) -> str:
    """Download a PDF and extract text (truncated for embedding / payload limits)."""
    if not pdf_url or not str(pdf_url).strip():
        return ""
    raw, err = _fetch_pdf_bytes(str(pdf_url).strip())
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


def extract_company_announcements():
    """Returns raw NSE corporate announcements (list of dicts)."""
    print("[Company][Extract] Requesting NSE company announcements")
    print("[Company][Extract] Creating session and loading announcements")
    _ensure_announcements_loaded()
    assert response is not None
    if response.status_code != 200:
        print(f"[Company][Extract] Failed (HTTP {response.status_code})")
        return []
    print("[Company][Extract] Parsing response data")
    data = response.json()
    print(f"[Company][Extract] Retrieved {len(data)} announcements")
    if data:
        print("[Company][Extract] First record preview:")
        print(json.dumps(data[0], indent=2))
    return data


if __name__ == "__main__":
    _ensure_announcements_loaded()
    print(nse_base_url)
    print(company_announcements_url)
    print("Status Code:", response.status_code if response else None)
    if response is not None and response.status_code == 200:
        data = response.json()
        print(json.dumps(data[0], indent=2))
        print(f"\nTotal Announcements: {len(data)}")
        for announcement in data:
            pdf_url = announcement.get("attchmntFile")
            print(extract_pdf_text(pdf_url))
            print("--------------------------------")
    else:
        print(response.text if response else "")
