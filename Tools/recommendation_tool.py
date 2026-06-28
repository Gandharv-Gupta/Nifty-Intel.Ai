import os
import requests
from langchain.tools import tool
import yfinance as yf

# from utils import load_repo_dotenv
from langchain.tools import tool
from recommendation_engine import recommend_stock

# load_repo_dotenv()

# alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
# alpha_vantage_base_url = os.getenv("ALPHA_VANTAGE_BASE_URL")

# def fetch_alpha_vantage(function: str, symbol: str, **kwargs):
#     params = {
#         "function": function,
#         "symbol": symbol,
#         "apikey": alpha_vantage_api_key,
#         **kwargs
#     }

#     print(f"[AlphaVantage][Fetch] Fetching {function} for {symbol}")

#     response = requests.get(
#         alpha_vantage_base_url,
#         params=params,
#         timeout=15
#     )
#     response.raise_for_status()

#     data = response.json()

#     # Keep only the latest value for technical indicators
#     technical_keys = [
#         "Technical Analysis: RSI",
#         "Technical Analysis: MACD",
#         "Technical Analysis: SMA",
#         "Technical Analysis: EMA"
#     ]

#     for key in technical_keys:
#         if key in data:
#             latest_date = next(iter(data[key]))
#             data[key] = {
#                 latest_date: data[key][latest_date]
#             }
#             break

#     return data


# @tool
# def get_recommendation_data(symbol: str) -> dict:
#     """
#     Fetch company fundamentals and technical indicators
#     for a stock from Alpha Vantage.

#     Args:
#         symbol: Stock symbol (e.g. INFY, RELIANCE, TCS)

#     Returns:
#         Dictionary containing all fetched data.
#     """
#     try:

#         return {
#             "overview": fetch_alpha_vantage(
#                 function="OVERVIEW",
#                 symbol=symbol
#             ),

#             "rsi": fetch_alpha_vantage(
#                 function="RSI",
#                 symbol=symbol,
#                 interval="daily",
#                 time_period=14,
#                 series_type="close"
#             ),

#             "macd": fetch_alpha_vantage(
#                 function="MACD",
#                 symbol=symbol,
#                 interval="daily",
#                 series_type="close"
#             ),

#             "sma_50": fetch_alpha_vantage(
#                 function="SMA",
#                 symbol=symbol,
#                 interval="daily",
#                 time_period=50,
#                 series_type="close"
#             )
#         }
#     except Exception as e:
#         return f"Error fetching recommendation data{e}"







# @tool
# def get_recommendation_data_tool(symbol: str) -> dict:
#     """
#     Fetch company fundamentals and recent data from Yahoo Finance.

#     Args:
#         symbol: NSE stock symbol (e.g. INFY, TCS, RELIANCE)

#     Returns:
#         Dictionary containing company fundamentals.
#     """

#     try:
#         ticker = yf.Ticker(f"{symbol}.NS")

#         info = ticker.info
#         fast_info = ticker.fast_info
#         news = ticker.news[:5]

#         return {
#             "symbol": symbol.upper(),

#             "company": {
#                 "name": info.get("longName"),
#                 "sector": info.get("sector"),
#                 "industry": info.get("industry"),
#                 "website": info.get("website"),
#                 "country": info.get("country"),
#                 "exchange": info.get("exchange"),
#                 "currency": info.get("currency"),
#                 "employees": info.get("fullTimeEmployees"),
#                 "business_summary": info.get("longBusinessSummary"),
#             },

#             "valuation": {
#                 "market_cap": info.get("marketCap"),
#                 "enterprise_value": info.get("enterpriseValue"),
#                 "pe_ratio": info.get("trailingPE"),
#                 "forward_pe": info.get("forwardPE"),
#                 "peg_ratio": info.get("pegRatio"),
#                 "price_to_book": info.get("priceToBook"),
#                 "book_value": info.get("bookValue"),
#                 "eps": info.get("trailingEps"),
#                 "beta": info.get("beta"),
#                 "dividend_yield": info.get("dividendYield"),
#             },

#             "profitability": {
#                 "profit_margin": info.get("profitMargins"),
#                 "gross_margin": info.get("grossMargins"),
#                 "operating_margin": info.get("operatingMargins"),
#                 "return_on_equity": info.get("returnOnEquity"),
#                 "return_on_assets": info.get("returnOnAssets"),
#             },

#             "growth": {
#                 "revenue_growth": info.get("revenueGrowth"),
#                 "earnings_growth": info.get("earningsGrowth"),
#             },

#             "financials": {
#                 "total_revenue": info.get("totalRevenue"),
#                 "ebitda": info.get("ebitda"),
#                 "free_cashflow": info.get("freeCashflow"),
#                 "operating_cashflow": info.get("operatingCashflow"),
#                 "total_cash": info.get("totalCash"),
#                 "total_debt": info.get("totalDebt"),
#             },

#             "price": {
#                 "current_price": fast_info.get("lastPrice"),
#                 "previous_close": info.get("previousClose"),
#                 "open": info.get("open"),
#                 "day_high": info.get("dayHigh"),
#                 "day_low": info.get("dayLow"),
#                 "fifty_day_average": info.get("fiftyDayAverage"),
#                 "two_hundred_day_average": info.get("twoHundredDayAverage"),
#                 "52_week_high": info.get("fiftyTwoWeekHigh"),
#                 "52_week_low": info.get("fiftyTwoWeekLow"),
#                 "average_volume": info.get("averageVolume"),
#                 "average_volume_10_day": info.get("averageVolume10days"),
#             },

#             "ownership": {
#                 "shares_outstanding": info.get("sharesOutstanding"),
#                 "float_shares": info.get("floatShares"),
#                 "institutional_holding": info.get("heldPercentInstitutions"),
#                 "insider_holding": info.get("heldPercentInsiders"),
#             },

#             "analyst": {
#                 "recommendation": info.get("recommendationKey"),
#                 "recommendation_mean": info.get("recommendationMean"),
#                 "target_mean_price": info.get("targetMeanPrice"),
#                 "target_high_price": info.get("targetHighPrice"),
#                 "target_low_price": info.get("targetLowPrice"),
#             },

#             "news": [
#                 {
#                     "title": article.get("content", {}).get("title"),
#                     "publisher": article.get("content", {}).get("provider", {}).get("displayName"),
#                 }
#                 for article in news
#             ]
#         }

#     except Exception as e:
#         return {"error": str(e)}



@tool
def get_recommendation_engine_tool(symbol: str) -> dict:
    """
    Fetch company fundamentals from Yahoo Finance and generate
    a configurable recommendation using the rule engine.
    """

    try:
        ticker = yf.Ticker(f"{symbol}.NS")

        info = ticker.info
        fast_info = ticker.fast_info
        news = ticker.news[:5]

        stock_data = {
            "symbol": symbol.upper(),

            "company": {
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "website": info.get("website"),
                "country": info.get("country"),
                "exchange": info.get("exchange"),
                "currency": info.get("currency"),
                "employees": info.get("fullTimeEmployees"),
                "business_summary": info.get("longBusinessSummary"),
            },

            "valuation": {
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "book_value": info.get("bookValue"),
                "eps": info.get("trailingEps"),
                "beta": info.get("beta"),
                "dividend_yield": info.get("dividendYield"),
            },

            "profitability": {
                "profit_margin": info.get("profitMargins"),
                "gross_margin": info.get("grossMargins"),
                "operating_margin": info.get("operatingMargins"),
                "return_on_equity": info.get("returnOnEquity"),
                "return_on_assets": info.get("returnOnAssets"),
            },

            "growth": {
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
            },

            "financials": {
                "total_revenue": info.get("totalRevenue"),
                "ebitda": info.get("ebitda"),
                "free_cashflow": info.get("freeCashflow"),
                "operating_cashflow": info.get("operatingCashflow"),
                "total_cash": info.get("totalCash"),
                "total_debt": info.get("totalDebt"),
            },

            "price": {
                "current_price": fast_info.get("lastPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "fifty_day_average": info.get("fiftyDayAverage"),
                "two_hundred_day_average": info.get("twoHundredDayAverage"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "average_volume": info.get("averageVolume"),
                "average_volume_10_day": info.get("averageVolume10days"),
            },

            "ownership": {
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "institutional_holding": info.get("heldPercentInstitutions"),
                "insider_holding": info.get("heldPercentInsiders"),
            },

            "analyst": {
                "recommendation": info.get("recommendationKey"),
                "recommendation_mean": info.get("recommendationMean"),
                "target_mean_price": info.get("targetMeanPrice"),
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
            },

            "news": [
                {
                    "title": article.get("content", {}).get("title"),
                    "publisher": article.get("content", {})
                                      .get("provider", {})
                                      .get("displayName"),
                }
                for article in news
            ]
        }

        # Call your configurable recommendation engine
        recommendation = recommend_stock(stock_data)

        return {
            "stock_data": stock_data,
            "recommendation_engine": recommendation
        }

    except Exception as e:
        return {
            "error": str(e)
        }

if __name__ == "__main__":
        # print(get_recommendation_data.invoke({"symbol": "INFY"}))
        print(get_recommendation_data_tool.invoke({"symbol": "INFY"}))