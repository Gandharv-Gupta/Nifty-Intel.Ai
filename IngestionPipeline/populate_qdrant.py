from IngestionPipeline import extract_nifty_50_data
from IngestionPipeline import extract_nifty_option_data
from IngestionPipeline import store_market_data
from IngestionPipeline import store_option_chain_data
from IngestionPipeline import extract_company_data
from IngestionPipeline import store_company_data

def populate_qdrant():
    print("[Pipeline] Starting Qdrant ingestion")

    print("[Pipeline] Step 1/3: Nifty 50 extraction and storage")
    nifty_50_data = extract_nifty_50_data()
    store_market_data(nifty_50_data)

    print("[Pipeline] Step 2/3: Nifty option extraction and storage")
    nifty_option_data = extract_nifty_option_data()
    store_option_chain_data(nifty_option_data)

    print("[Pipeline] Step 3/3: Company data extraction and storage")
    company_data = extract_company_data()
    store_company_data(company_data)

    print("[Pipeline] Qdrant ingestion completed")


if __name__ == "__main__":
    populate_qdrant()