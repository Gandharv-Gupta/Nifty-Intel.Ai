import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

nifty_50_base_url = os.getenv("NIFTY_50_BASE_URL")
nifty_50_api_url = os.getenv("NIFTY_50_API_URL")

print(nifty_50_base_url)
print(nifty_50_api_url)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()

# Visit NSE homepage first to obtain cookies
session.get(nifty_50_base_url, headers=headers, timeout=10)

# Fetch Nifty 50 data
response = session.get(nifty_50_api_url, headers=headers, timeout=10)

print("Status Code:", response.status_code)



if response.status_code == 200:
    data = response.json()

    # Print first company record
    print(json.dumps(data["data"][0], indent=2))
    print(f"\nTotal Companies: {len(data['data'])}")
else:
    print(response.text)


def extract_nifty_50_data():
    return response.json()
