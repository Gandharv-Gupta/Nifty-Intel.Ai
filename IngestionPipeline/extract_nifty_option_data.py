# https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry=23-Jun-2026


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

def extract_nifty_option_data():
    nifty_option_base_url = os.getenv("NIFTY_OPTION_BASE_URL")
    nifty_option_api_url = os.getenv("NIFTY_OPTION_API_URL")
    option_expiry_date = os.getenv("OPTION_EXPIRY_DATE")

    print("[NiftyOption][Extract] Requesting NSE option-chain data")
    print("[NiftyOption][Extract] Creating session")

    params = {
        "expiry": option_expiry_date,
    }

    session = requests.Session()
    print("[NiftyOption][Extract] Fetching option-chain snapshot")
    session.get(nifty_option_base_url, headers=headers, timeout=10)
    response = session.get(nifty_option_api_url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        print(f"[NiftyOption][Extract] Failed (HTTP {response.status_code})")
        return {"records": {"data": []}}

    print("[NiftyOption][Extract] Parsing response data")
    data = response.json()
    option_records = data.get("records", {}).get("data", [])
    print(f"[NiftyOption][Extract] Retrieved {len(option_records)} records")
    if option_records:
        print("[NiftyOption][Extract] First record preview:")
        print(json.dumps(option_records[0], indent=2))

    return data
