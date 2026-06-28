#Run ingestion pipeline with:
python -m IngestionPipeline.populate_qdrant

#Run backend:
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000

#Nifty chat UI (streams POST /chat over SSE):
# http://127.0.0.1:8000/nifty/

#Ingest data individually in the qdrant:
python -u IngestionPipeline/ingest_company_data.py

#Ingest all
python -u -m IngestionPipeline.populate_qdrant

#Run ingestion pipeline



#Indicators I am fetching:
OVERVIEW: Company fundamentals (PE, EPS, Market Cap, Sector, Beta)
RSI:  momentum indicator
MAC:  trend indicator
SMA	:Confirms trend (e.g., 50-day SMA)
