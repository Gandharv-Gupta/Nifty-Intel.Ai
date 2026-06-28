import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

def extract_nifty_50_data():
    nifty_50_base_url = os.getenv("NIFTY_50_BASE_URL")
    nifty_50_api_url = os.getenv("NIFTY_50_API_URL")

    print("[Nifty50][Extract] Requesting NSE market data")
    print("[Nifty50][Extract] Creating session")

    session = requests.Session()
    print("[Nifty50][Extract] Fetching market snapshot")
    session.get(nifty_50_base_url, headers=headers, timeout=10)
    response = session.get(nifty_50_api_url, headers=headers, timeout=10)

    if response.status_code != 200:
        print(f"[Nifty50][Extract] Failed (HTTP {response.status_code})")
        return {"data": []}

    print("[Nifty50][Extract] Parsing response data")
    data = response.json()
    market_records = data.get("data", [])
    print(f"[Nifty50][Extract] Retrieved {len(market_records)} records")
    if market_records:
        print("[Nifty50][Extract] First record preview:")
        print(json.dumps(market_records[0], indent=2))

    return data
