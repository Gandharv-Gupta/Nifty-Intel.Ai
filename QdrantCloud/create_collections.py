import os
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType
)

load_dotenv()

qdrant_url = os.getenv("QDRANT_CLUSTER_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_collection_name_nifty_50 = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_50")
qdrant_collection_name_nifty_option = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_OPTION")
qdrant_collection_name_company_documents = os.getenv("QDRANT_COLLECTION_NAME_COMPANY_DOCUMENTS")

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

VECTOR_SIZE = 384  # all-MiniLM-L6-v2


def create_collection_if_not_exists(collection_name: str):
    existing = [c.name for c in client.get_collections().collections]

    if collection_name in existing:
        print(f" Collection already exists: {collection_name}")
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )

    print(f" Created collection: {collection_name}")


create_collection_if_not_exists(qdrant_collection_name_nifty_50)
create_collection_if_not_exists(qdrant_collection_name_nifty_option)
create_collection_if_not_exists(qdrant_collection_name_company_documents)

#Market data indexes

try:
# Symbol (INFY, TCS, RELIANCE...)
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_50,
        field_name="symbol",
        field_schema=PayloadSchemaType.KEYWORD
    )

    # Market date
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_50,
        field_name="market_date",
        field_schema=PayloadSchemaType.KEYWORD
    )

    # Source (market_data vs other payloads) — enables future server-side filters
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_50,
        field_name="source",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    # Percentage change
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_50,
        field_name="pchange",
        field_schema=PayloadSchemaType.FLOAT
    )

    # Volume
    client.create_payload_index(
        collection_name="nifty50_market_data",
        field_name="volume",
        field_schema=PayloadSchemaType.INTEGER
    )

    # Last traded price
    client.create_payload_index(
        collection_name="nifty50_market_data",
        field_name="last_price",
        field_schema=PayloadSchemaType.FLOAT
    )

except Exception as e:
    print(f"Market indexes may already exist: {e}")


#Option chain indexes

try:
    # Underlying symbol (NIFTY)
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="symbol",
        field_schema=PayloadSchemaType.KEYWORD
    )

    # Expiry date
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="expiry",
        field_schema=PayloadSchemaType.KEYWORD
    )

    # Strike price
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="strike_price",
        field_schema=PayloadSchemaType.INTEGER
    )

    # Call Open Interest
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="ce_oi",
        field_schema=PayloadSchemaType.INTEGER
    )

    # Put Open Interest
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="pe_oi",
        field_schema=PayloadSchemaType.INTEGER
    )

    # Call Volume
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="ce_volume",
        field_schema=PayloadSchemaType.INTEGER
    )

    # Put Volume
    client.create_payload_index(
        collection_name=qdrant_collection_name_nifty_option,
        field_name="pe_volume",
        field_schema=PayloadSchemaType.INTEGER
    )
except Exception as e:
    print(f"Option indexes may already exist: {e}")


#Company documents indexes

try:
    client.create_payload_index(
        collection_name=qdrant_collection_name_company_documents,
        field_name="company",
        field_schema=PayloadSchemaType.KEYWORD
    )

    client.create_payload_index(
        collection_name=qdrant_collection_name_company_documents,
        field_name="document_type",
        field_schema=PayloadSchemaType.KEYWORD
    )

    client.create_payload_index(
        collection_name=qdrant_collection_name_company_documents,
        field_name="document_date",
        field_schema=PayloadSchemaType.KEYWORD
    )

    client.create_payload_index(
        collection_name=qdrant_collection_name_company_documents,
        field_name="source",
        field_schema=PayloadSchemaType.KEYWORD
    )

    print(" Company document indexes created")

except Exception as e:
    print(f"Document indexes may already exist: {e}")


print("\n Qdrant collections and indexes created successfully!")