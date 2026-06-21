from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, message_to_dict
import json


def load_repo_dotenv() -> None:
    """Load repo-root `.env` regardless of process cwd (e.g. `python IngestionPipeline/...`)."""
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")


def json_safe(value: Any) -> Any:
    """Turn invoke/stream payloads into JSON-serializable data."""
    if isinstance(value, BaseMessage):
        return message_to_dict(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "model_dump"):
        try:
            return json_safe(value.model_dump(mode="json"))
        except Exception:
            return json_safe(value.model_dump())
    return str(value)

def _sse(data: dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _text_from_llm_token(token: Any) -> str:
    """Extract incremental text from LangGraph `stream_mode='messages'` tokens."""
    if token is None:
        return ""
    # `stream_mode="messages"` also emits ToolMessage / HumanMessage etc. from node outputs.
    # Only forward assistant text so clients never see raw tool payloads.
    if not isinstance(token, AIMessage):
        return ""
    content = getattr(token, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    if content is not None:
        return str(content)
    return ""


NIFTY_50_SYMBOLS = {
    "ADANIPORTS",
    "ASIANPAINT",
    "AXISBANK",
    "BAJAJ-AUTO",
    "BAJFINANCE",
    "BAJAJFINSV",
    "BEL",
    "BHARTIARTL",
    "CIPLA",
    "COALINDIA",
    "DRREDDY",
    "EICHERMOT",
    "ETERNAL",
    "GRASIM",
    "HCLTECH",
    "HDFCBANK",
    "HDFCLIFE",
    "HEROMOTOCO",
    "HINDALCO",
    "HINDUNILVR",
    "ICICIBANK",
    "INDUSINDBK",
    "INFY",
    "ITC",
    "JIOFIN",
    "JSWSTEEL",
    "KOTAKBANK",
    "LT",
    "M&M",
    "MARUTI",
    "NESTLEIND",
    "NTPC",
    "ONGC",
    "POWERGRID",
    "RELIANCE",
    "SBILIFE",
    "SBIN",
    "SHRIRAMFIN",
    "SUNPHARMA",
    "TATACONSUM",
    "TATAMOTORS",
    "TATASTEEL",
    "TCS",
    "TECHM",
    "TITAN",
    "TRENT",
    "ULTRACEMCO",
    "WIPRO"
}