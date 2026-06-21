# NiftyIntel AI 📈🤖

An Agentic RAG system for the Indian stock market that collects NIFTY 50 market data, option chain data, and corporate announcements, stores them in a vector database, and enables natural-language querying through an AI-powered chatbot.

---

## Overview

NiftyIntel AI is an end-to-end market intelligence platform built around Agentic AI and Retrieval-Augmented Generation (RAG).

The system automatically ingests daily market data from NSE, processes both structured and unstructured financial information (including PDF announcements), generates vector embeddings, and stores everything in Qdrant for semantic retrieval.

Users can interact with the system using natural language to:

* Analyze NIFTY 50 market movements
* Explore option chain activity
* Identify top gainers and losers
* Query company announcements
* Extract insights from PDFs
* Generate AI-driven market analysis

---

## Architecture

```text
NSE APIs
    │
    ▼
Data Ingestion Pipeline
    │
    ├── Market Data
    ├── Option Chain Data
    └── Corporate Announcements + PDFs
    │
    ▼
Processing Layer
    │
    ├── Cleaning
    ├── PDF Extraction
    ├── Chunking
    └── Embedding Generation
    │
    ▼
Qdrant Vector Database
    │
    ▼
LangGraph Agent
    │
    ├── Market Data Tool
    ├── Option Chain Tool
    ├── Top Gainers/Losers Tool
    ├── Company Documents Tool
    └── Analytics Tool
    │
    ▼
LLM Reasoning
    │
    ▼
Natural Language Responses
```

---

## Features

### Daily NIFTY 50 Market Data Collection

Collects live market information including:

* Symbol
* Last Price
* Open
* High
* Low
* Volume
* Traded Value
* Percentage Change
* 52 Week High/Low

Example:

```text
INFY
Last Price: 1054.20
Change: -6.50%
Volume: 45,665,442
```

---

### Option Chain Intelligence

Tracks option chain data such as:

* Strike Price
* Open Interest (OI)
* Change in OI
* Call Option Metrics
* Put Option Metrics
* Implied Volatility
* Trading Volume

Example Questions:

```text
What is the highest OI strike for NIFTY?

Which strikes have significant Put writing?
```

---

### Corporate Announcements Processing

Automatically ingests:

* NSE corporate announcements
* Attached PDFs
* ZIP documents
* Investor presentations
* Board meeting updates
* AGM notices
* Earnings reports

The system:

1. Downloads documents
2. Extracts text
3. Generates embeddings
4. Stores them in Qdrant
5. Makes them searchable through RAG

Example:

```text
Summarize the latest announcement from INFY.
```

---

### Agentic AI

Built using LangGraph.

The central NiftyAgent dynamically decides which tools to invoke based on the user's question.

#### Available Tools

| Tool                    | Purpose                     |
| ----------------------- | --------------------------- |
| Market Data Tool        | Retrieve market data        |
| Option Chain Tool       | Query option chain records  |
| Top Gainers/Losers Tool | Market performance analysis |
| Company Documents Tool  | PDF retrieval and analysis  |
| Analytics Tool          | AI-powered reasoning        |

---

## Tech Stack

### AI & LLM

* LangGraph
* LangChain
* OpenAI GPT-4o
* Google Gemini
* Sentence Transformers

### Vector Database

* Qdrant

### Backend

* Python
* FastAPI

### Data Sources

* NSE Market APIs
* NSE Option Chain APIs
* NSE Corporate Announcement APIs

### Document Processing

* PyMuPDF
* PDF Extraction
* Text Chunking

### Embeddings

```text
sentence-transformers/all-MiniLM-L6-v2
```

---

## Qdrant Collections

### 1. nifty50_market_data

Stores structured market data.

Example Metadata:

```json
{
  "symbol": "INFY",
  "last_price": 1054.2,
  "change": -73.3,
  "pchange": -6.5
}
```

---

### 2. nifty50_option_chain

Stores option chain records.

Example Metadata:

```json
{
  "strike_price": 24000,
  "expiry_date": "23-Jun-2026",
  "call_oi": 500000,
  "put_oi": 800000
}
```

---

### 3. nifty50_company_documents

Stores processed corporate announcements and PDF content.

Example Metadata:

```json
{
  "symbol": "INFY",
  "announcement_type": "Investor Presentation",
  "pdf_url": "...",
  "announcement_date": "2026-06-21"
}
```

---

## Project Structure

```text
NiftyIntelAI/
│
├── agents/
│   └── nifty_agent.py
│
├── tools/
│   ├── market_data_tool.py
│   ├── option_chain_tool.py
│   ├── top_gainers_tool.py
│   ├── company_documents_tool.py
│   └── analytics_tool.py
│
├── ingestion/
│   ├── market_data/
│   ├── option_chain/
│   └── corporate_announcements/
│
├── embeddings/
│
├── vector_store/
│   └── qdrant/
│
├── api/
│
├── shared/
│
├── tests/
│
├── requirements.txt
│
└── README.md
```

---

## Example Queries

### Market Data

```text
Which NIFTY 50 stocks gained the most today?
```

```text
Show me the latest data for INFY.
```

---

### Option Chain

```text
What is the highest open interest strike?
```

```text
Which strikes indicate strong support?
```

---

### Corporate Documents

```text
Summarize the latest announcement from AXISBANK.
```

```text
What did INFY announce recently?
```

---

### Analytics

```text
Analyze today's market sentiment.
```

```text
Compare NIFTY market data with option chain activity.
```

---

## Future Enhancements

* Historical trend analysis
* Multi-day option chain tracking
* Company-level financial intelligence
* Advanced forecasting
* Portfolio insights
* Real-time streaming updates
* Multi-agent architecture
* Hybrid search (Vector + Metadata)

---

## Why This Project?

Financial data is fragmented across multiple sources and formats.

NiftyIntel AI combines:

* Structured market data
* Option chain analytics
* Unstructured PDF documents
* Vector search
* Agentic AI

into a single intelligent system capable of answering complex financial questions through natural language.

---

## Author

**Gandharv Gupta**

AI Engineer | Generative AI | Agentic Systems | RAG Applications


