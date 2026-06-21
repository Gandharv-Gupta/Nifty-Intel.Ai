import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

from shared_qdrant import client
from dotenv import load_dotenv

load_dotenv()

qdrant_collection_name_company_documents = os.getenv(
    "QDRANT_COLLECTION_NAME_COMPANY_DOCUMENTS"
)

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def build_company_text(announcement: dict) -> str:
    return f"""
    Company Symbol: {announcement.get('symbol')}
    Company Name: {announcement.get('sm_name')}

    Announcement Type:
    {announcement.get('desc')}

    Announcement Details:
    {announcement.get('attchmntText')}

    Announcement Date:
    {announcement.get('an_dt')}
    """.strip()


def store_company_data(announcements: list):

    announcement_date = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d")

    points = []

    for announcement in announcements:

        text = build_company_text(announcement)

        vector = embedding_model.encode(text).tolist()

        payload = {
            "source": "company_announcements",

            "announcement_date": announcement_date,

            "symbol": announcement.get("symbol"),

            "company_name": announcement.get("sm_name"),

            "announcement_type": announcement.get("desc"),

            "announcement_text": announcement.get(
                "attchmntText"
            ),

            "pdf_url": announcement.get(
                "attchmntFile"
            ),

            "announcement_time": announcement.get(
                "an_dt"
            ),

            "file_size": announcement.get(
                "fileSize"
            ),

            "has_xbrl": announcement.get(
                "hasXbrl"
            ),

            "ingested_at": datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).isoformat(),

            "raw_record": announcement
        }

        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=payload
            )
        )

    client.upsert(
        collection_name=qdrant_collection_name_company_documents,
        points=points
    )

    print(
        f"Stored {len(points)} records in "
        f"'{qdrant_collection_name_company_documents}'"
    )


if __name__ == "__main__":
    import extract_company_data as ec

    if getattr(ec, "response", None) is None or ec.response.status_code != 200:
        print("Company announcements fetch did not succeed; nothing ingested.")
        sys.exit(1)

    announcements = ec.extract_company_announcements()
    if not isinstance(announcements, list) or not announcements:
        print("No announcements list in response; nothing ingested.")
        sys.exit(1)

    store_company_data(announcements)