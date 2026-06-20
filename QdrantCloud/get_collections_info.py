from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv


load_dotenv()

qdrant_collection_name_nifty_50 = os.getenv("QDRANT_COLLECTION_NAME_NIFTY_50")
qdrant_url = os.getenv("QDRANT_CLUSTER_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")


client = QdrantClient(
    url=os.getenv("QDRANT_CLUSTER_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

#Print all collections
print(client.get_collections())
#Print info of a collection
info = client.get_collection(qdrant_collection_name_nifty_50)
print(info)
