# https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry=23-Jun-2026


import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

nifty_option_base_url = os.getenv("NIFTY_OPTION_BASE_URL")
nifty_option_api_url = os.getenv("NIFTY_OPTION_API_URL")
option_expiry_date = os.getenv("OPTION_EXPIRY_DATE")

print(nifty_option_base_url)
print(nifty_option_api_url)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

params = {
    "expiry": option_expiry_date,
}

session = requests.Session()

# Visit NSE homepage first to obtain cookies
session.get(nifty_option_base_url, headers=headers, timeout=10)

# Fetch Nifty 50 data
response = session.get(nifty_option_api_url, headers=headers, params=params, timeout=10)

print("Status Code:", response.status_code)
if response.status_code == 200:
    data = response.json()
    print(data.keys())

    # Print first company record
    print(json.dumps(data["records"].get("data")[0], indent=2))
    print(f"\nTotal Companies: {len(data['records'].get('data'))}")
else:
    print(response.text)


def extract_nifty_option_data():
    return response.json()
