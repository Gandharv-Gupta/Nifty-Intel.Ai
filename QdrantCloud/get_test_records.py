from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

load_dotenv()

qdrant_collection_name_nifty_50 = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_50")
qdrant_url = os.getenv("QDRANT_CLUSTER_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)


records, next_page = client.scroll(
    collection_name=qdrant_collection_name_nifty_50,
    limit=5,
    with_payload=True,
    with_vectors=False
)

for record in records:
    print("\n-------------------")
    print("ID:", record.id)
    print("Payload:", record.payload)