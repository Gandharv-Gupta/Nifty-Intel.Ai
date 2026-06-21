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

from utils import load_repo_dotenv
from shared_qdrant import client
from extract_company_data import extract_pdf_text

load_repo_dotenv()

qdrant_collection_name_company_documents = os.getenv(
    "QDRANT_COLLECTION_NAME_COMPANY_DOCUMENTS"
)

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def build_company_text(announcement: dict, pdf_extract: str = "") -> str:
    base = f"""
    Company Symbol: {announcement.get('symbol')}
    Company Name: {announcement.get('sm_name')}

    Announcement Type:
    {announcement.get('desc')}

    Announcement Details:
    {announcement.get('attchmntText')}

    Announcement Date:
    {announcement.get('an_dt')}
    """.strip()
    pe = (pdf_extract or "").strip()
    if pe and not pe.startswith("Unable to download PDF"):
        return f"{base}\n\nAttachment PDF text:\n{pe}"
    return base


def store_company_data(announcements: list):

    announcement_date = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d")

    points = []

    for announcement in announcements:

        pdf_url = announcement.get("attchmntFile")
        pdf_extract = ""
        pdf_extraction_error = None
        if pdf_url:
            raw = extract_pdf_text(pdf_url)
            if isinstance(raw, str) and raw.startswith("Unable to download PDF"):
                pdf_extraction_error = raw
            else:
                pdf_extract = raw or ""

        text = build_company_text(announcement, pdf_extract)

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

            "pdf_extracted_text": (
                (pdf_extract[:12000] if len(pdf_extract) > 12000 else pdf_extract)
                if pdf_extract
                else None
            ),

            "pdf_extraction_error": pdf_extraction_error,

            "raw_record": announcement,
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

    announcements = ec.extract_company_announcements()
    if not isinstance(announcements, list) or not announcements:
        print("Company announcements fetch did not return data; nothing ingested.")
        sys.exit(1)

    store_company_data(announcements)