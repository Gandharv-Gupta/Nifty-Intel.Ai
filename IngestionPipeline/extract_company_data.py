import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

nse_base_url = os.getenv("NSE_BASE_URL")
company_announcements_url = os.getenv(
    "NSE_COMPANY_ANNOUNCEMENTS_URL"
)

print(nse_base_url)
print(company_announcements_url)

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

# Get NSE cookies
session.get(
    nse_base_url,
    headers=headers,
    timeout=10
)

# Fetch announcements
response = session.get(
    company_announcements_url,
    headers=headers,
    timeout=10
)

print("Status Code:", response.status_code)

if response.status_code == 200:

    data = response.json()

    print(
        json.dumps(
            data[0],
            indent=2
        )
    )

    print(
        f"\nTotal Announcements: {len(data)}"
    )

else:
    print(response.text)


def extract_company_announcements():
    """
    Returns raw NSE corporate announcements.
    """
    return response.json()