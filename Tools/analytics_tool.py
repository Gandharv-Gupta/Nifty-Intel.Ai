import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

openai_model = os.getenv("OPENAI_MODEL")
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = init_chat_model(
    f"openai:{openai_model}",
    api_key=openai_api_key,
)


@tool
def analyze_market(context: str):
    """
    LLM-based commentary on market data you already fetched (does NOT call Qdrant).
    Pass a structured summary: paste JSON or key fields from get_market_data,
    get_top_movers, and/or get_option_chain into `context` first.
    Input:
    context: str = Verbatim or summarized numeric output from the other tools (non-empty).
    Output:
    str = Short analysis (summary, insights, risk framing). Not investment advice.
    """
    raw = (context or "").strip()
    if not raw:
        return (
            "No data in context. Call get_market_data and/or get_top_movers first, "
            "then call analyze_market with their returned text pasted into context."
        )

    system = SystemMessage(
        content=(
            "You are a financial analyst. Given ONLY the user-supplied market snapshot below, "
            "provide: (1) Summary (2) Key insights (3) Risk signals if any. "
            "Use cautious language; this is snapshot data, not investment advice."
        )
    )
    human = HumanMessage(
        content=f"Market snapshot to analyze:\n\n{raw}\n\nRespond with Summary, Key insights, and Risk signals."
    )

    response = llm.invoke([system, human])
    return response.content
