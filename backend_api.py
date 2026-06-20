from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, BaseMessage, message_to_dict
from pydantic import BaseModel, Field

load_dotenv()

from agent import nifty_agent

logger = logging.getLogger(__name__)

app = FastAPI(title="NiftyIntel API", version="0.1.0")

CHAT_STREAM_CHUNK_SIZE = 32
CHAT_STREAM_CHUNK_DELAY_SECONDS = 0


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)


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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    """Stream model tokens over SSE, then a minimal terminal event (`done: true`)."""

    async def generate_response() -> AsyncIterator[str]:
        query = req.query.strip()
        inputs = {"messages": [{"role": "user", "content": query}]}
        last_tool_name = ""
        try:
            async for event in nifty_agent.astream(
                inputs,
                stream_mode=["messages", "tools"],
            ):
                if isinstance(event, tuple) and len(event) == 3:
                    _, mode, payload = event[0], event[1], event[2]
                elif isinstance(event, tuple) and len(event) == 2:
                    mode, payload = event[0], event[1]
                else:
                    continue
                if mode == "tools" and isinstance(payload, dict):
                    ev = payload.get("event")
                    if ev == "tool-started":
                        last_tool_name = str(
                            payload.get("tool_name") or payload.get("name") or "tool"
                        )
                        yield _sse(
                            {
                                "content": "",
                                "done": False,
                                "tool": last_tool_name,
                                "tool_phase": "running",
                            }
                        )
                    elif ev == "tool-finished":
                        yield _sse(
                            {
                                "content": "",
                                "done": False,
                                "tool": last_tool_name or None,
                                "tool_phase": "idle",
                            }
                        )
                    elif ev == "tool-error":
                        yield _sse(
                            {
                                "content": "",
                                "done": False,
                                "tool": last_tool_name or None,
                                "tool_phase": "error",
                                "tool_error": str(payload.get("message") or "tool error"),
                            }
                        )
                    continue
                if mode != "messages":
                    continue
                if isinstance(payload, tuple) and len(payload) >= 1:
                    token = payload[0]
                else:
                    token = payload
                text = _text_from_llm_token(token)
                if not text:
                    continue
                for i in range(0, len(text), CHAT_STREAM_CHUNK_SIZE):
                    chunk = text[i : i + CHAT_STREAM_CHUNK_SIZE]
                    yield _sse({"content": chunk, "done": False})
                    if CHAT_STREAM_CHUNK_DELAY_SECONDS > 0:
                        await asyncio.sleep(CHAT_STREAM_CHUNK_DELAY_SECONDS)

            yield _sse({"content": "", "done": True, "tool": None, "tool_phase": "idle"})
        except Exception as exc:
            logger.exception("chat stream failed")
            yield _sse(
                {
                    "content": "",
                    "done": True,
                    "error": str(exc),
                    "tool": None,
                    "tool_phase": "idle",
                }
            )

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.post("/chat/updates")
async def chat_updates(req: ChatRequest) -> StreamingResponse:
    """Optional: NDJSON stream of graph `updates` (debug / tooling)."""

    def generate_updates():
        inputs = {"messages": [{"role": "user", "content": req.query.strip()}]}
        try:
            for chunk in nifty_agent.stream(inputs, stream_mode="updates"):
                yield json.dumps(json_safe(chunk), ensure_ascii=False) + "\n"
        except Exception as exc:
            yield json.dumps({"error": str(exc)}, ensure_ascii=False) + "\n"

    return StreamingResponse(
        generate_updates(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/chat/sync")
async def chat_sync(req: ChatRequest) -> JSONResponse:
    """Run the agent to completion and return one JSON object."""
    inputs = {"messages": [{"role": "user", "content": req.query.strip()}]}
    try:
        result = nifty_agent.invoke(inputs)
        return JSONResponse(content=json_safe(result))
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


_NIFTY_UI_DIR = Path(__file__).resolve().parent / "static"
if _NIFTY_UI_DIR.is_dir():
    app.mount(
        "/nifty",
        StaticFiles(directory=str(_NIFTY_UI_DIR), html=True),
        name="nifty_chat_ui",
    )

