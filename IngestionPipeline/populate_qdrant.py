from IngestionPipeline import extract_nifty_50_data
from IngestionPipeline import extract_nifty_option_data
from IngestionPipeline import store_market_data
from IngestionPipeline import store_option_chain_data
from IngestionPipeline import extract_company_data
from IngestionPipeline import store_company_data

def populate_qdrant():
    nifty_50_data = extract_nifty_50_data()
    print("successfuly extracted nifty 50 data")
    store_market_data(nifty_50_data)
    print("successfuly ingested nifty 50 data")

    nifty_option_data = extract_nifty_option_data()
    print("successfuly extracted nifty option data")
    store_option_chain_data(nifty_option_data)
    print("successfuly ingested nifty option data")

    company_data = extract_company_data()
    print("successfuly extracted company data")
    store_company_data(company_data)
    print("successfuly ingested company data")


if __name__ == "__main__":
    populate_qdrant()