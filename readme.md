# NiftyIntel AI 📈🤖

An Agentic AI-powered market intelligence platform for the Indian stock market that combines Retrieval-Augmented Generation (RAG), automated data ingestion, semantic search, and configurable stock recommendations using LLMs and financial fundamentals.

---

# Overview

NiftyIntel AI is an end-to-end market intelligence platform built around Agentic AI and Retrieval-Augmented Generation (RAG).

The platform automatically ingests daily market data from NSE, processes both structured and unstructured financial information (including PDF announcements), generates vector embeddings, and stores everything in Qdrant for semantic retrieval.

It also includes a configurable stock recommendation engine that combines company fundamentals from Yahoo Finance with rule-based scoring and LLM reasoning.

Users can interact with the system using natural language to:

- Analyze NIFTY 50 market movements
- Explore option chain activity
- Identify top gainers and losers
- Query company announcements
- Extract insights from corporate PDFs
- Generate AI-powered market analysis
- Receive configurable stock recommendations

---

# Architecture

```mermaid
(Paste your Mermaid architecture here)
```

---

# Features

## Daily Automated Data Ingestion

The platform automatically refreshes its knowledge base using APScheduler.

Every scheduled run:

- Fetches NIFTY 50 market data
- Fetches NIFTY option chain
- Retrieves corporate announcements
- Downloads attached PDFs
- Extracts document text
- Chunks documents
- Generates embeddings
- Updates Qdrant collections

This ensures that the chatbot always operates on the latest market snapshot.

---

## NIFTY 50 Market Intelligence

Collects market information including:

- Symbol
- Last Price
- Open
- High
- Low
- Previous Close
- Volume
- Traded Value
- Percentage Change
- 52 Week High / Low

Example:

```text
Show me today's market data for INFY.
```

---

## Option Chain Intelligence

Tracks option chain metrics such as:

- Strike Price
- Open Interest
- Change in OI
- Call OI
- Put OI
- Volume
- Implied Volatility

Example:

```text
Which strike has the highest Call Open Interest?
```

---

## Corporate Announcement Intelligence

Automatically processes:

- NSE Corporate Announcements
- Investor Presentations
- Board Meeting Updates
- AGM Notices
- Financial Reports
- PDF Attachments
- ZIP Attachments

Pipeline:

1. Download document
2. Extract PDF text
3. Chunk content
4. Generate embeddings
5. Store in Qdrant
6. Retrieve using semantic search

Example:

```text
Summarize the latest announcement from INFY.
```

---

## AI-Powered Stock Recommendation Engine

The platform includes a configurable recommendation engine.

Workflow:

1. Fetch latest company fundamentals from Yahoo Finance
2. Apply configurable financial rules stored in YAML
3. Generate a recommendation score
4. Pass both the score and raw financial data to the LLM
5. Generate an explainable recommendation

Unlike pure LLM reasoning, recommendations remain transparent, deterministic, and easily tunable.

Example:

```text
Should I buy Infosys today?
```

---

# Agentic AI

Built using LangGraph.

The central **NiftyAgent** dynamically decides which tools to invoke depending on the user's request.

## Available Tools

| Tool | Purpose |
|------|---------|
| Market Data Tool | Retrieve latest NIFTY 50 market data |
| Option Chain Tool | Query option chain data |
| Top Gainers / Losers Tool | Market performance analysis |
| Company Documents Tool | Retrieve and summarize corporate announcements |
| Analytics Tool | AI-powered market reasoning |
| Recommendation Tool | Fetch fundamentals and generate configurable stock recommendations |

---

# Tech Stack

## AI

- LangGraph
- LangChain
- OpenAI GPT-4o
- Google Gemini

## Vector Database

- Qdrant

## Backend

- Python
- FastAPI

## Scheduling

- APScheduler

## Financial Data Sources

- NSE Market APIs
- NSE Option Chain APIs
- NSE Corporate Announcement APIs
- Yahoo Finance

## Embeddings

- sentence-transformers/all-MiniLM-L6-v2

## Document Processing

- PyMuPDF
- PDF Text Extraction
- Text Chunking

---

# Recommendation Rules

Recommendation logic is completely configurable using YAML.

Example:

```yaml
pe:
  excellent: 15
  acceptable: 25

roe:
  excellent: 0.20
  acceptable: 0.15

recommendation:
  strong_buy: 15
  buy: 10
  hold: 5
```

Changing the YAML changes the recommendation behaviour without modifying Python code.

---

# Qdrant Collections

## Market Data

Stores structured NIFTY 50 market snapshots.

Example metadata:

```json
{
  "symbol": "INFY",
  "last_price": 1054.2,
  "change": -73.3,
  "pchange": -6.5
}
```

---

## Option Chain

Stores option chain records.

Example:

```json
{
  "strike_price": 24000,
  "expiry_date": "23-Jun-2026",
  "call_oi": 500000,
  "put_oi": 800000
}
```

---

## Company Documents

Stores embedded corporate announcements and PDF content.

Example:

```json
{
  "symbol": "INFY",
  "announcement_type": "Investor Presentation",
  "announcement_date": "2026-06-21"
}
```

---

# Project Structure

```text
NiftyIntelAI/

├── agent.py

├── Tools/
│   ├── market_data_tool.py
│   ├── option_chain_tool.py
│   ├── top_movers_tool.py
│   ├── company_documents_tool.py
│   ├── analytics_tool.py
│   └── recommendation_tool.py

├── recommendation/
│   ├── recommendation_engine.py
│   └── recommendation_rules.yml

├── ingestion/
│   ├── market_data/
│   ├── option_chain/
│   └── corporate_announcements/

├── scheduler/
│   └── scheduler.py

├── qdrant/

├── shared/

├── requirements.txt

└── README.md
```

---

# Example Queries

## Market Data

```text
Which NIFTY 50 stocks gained the most today?
```

```text
Show me today's market data for INFY.
```

---

## Option Chain

```text
Which strike has the highest Open Interest?
```

```text
Where is the strongest support according to today's option chain?
```

---

## Company Announcements

```text
Summarize the latest announcement from AXISBANK.
```

```text
What did Infosys announce recently?
```

---

## Market Analysis

```text
Analyze today's market sentiment.
```

```text
Compare today's option chain with market movement.
```

---

## Stock Recommendations

```text
Should I buy Infosys today?
```

```text
Recommend a NIFTY 50 stock.
```

```text
Why do you recommend HDFC Bank?
```

```text
Compare Infosys and TCS from an investment perspective.
```

---

# Future Enhancements

- Portfolio-aware recommendations
- Technical indicators (RSI, MACD)
- Historical backtesting
- Multi-agent financial analyst system
- Real-time streaming updates
- Hybrid Vector + SQL retrieval
- Sector-wise recommendation engine

---

# Why This Project?

Financial information is fragmented across structured APIs, option chain data, company announcements, and lengthy PDF documents.

NiftyIntel AI unifies all of these into a single Agentic AI platform capable of:

- Semantic search over financial documents
- Market intelligence using RAG
- Automated daily data ingestion
- LLM-powered market analysis
- Explainable stock recommendations using configurable financial rules

---

# Author

**Gandharv Gupta**

AI Engineer | Generative AI | Agentic AI | Retrieval-Augmented Generation (RAG)