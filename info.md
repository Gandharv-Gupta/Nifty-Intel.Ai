#Run ingestion pipeline with:
python -m IngestionPipeline.populate_qdrant

#Run backend:
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000

#Nifty chat UI (streams POST /chat over SSE):
# http://127.0.0.1:8000/nifty/

#Ingest data individually in the qdrant:
python -u IngestionPipeline/ingest_company_data.py

