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
from utils import json_safe,_sse,_text_from_llm_token
from agent import nifty_agent
import os

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="NiftyIntel API", version="0.1.0")

chat_stream_chunk_size = int(os.getenv("CHAT_STREAM_CHUNK_SIZE"))
chat_stream_chunk_delay_seconds = float(os.getenv("CHAT_STREAM_CHUNK_DELAY_SECONDS"))


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)


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
                for i in range(0, len(text), chat_stream_chunk_size):
                    chunk = text[i : i + chat_stream_chunk_size]
                    yield _sse({"content": chunk, "done": False})
                    if chat_stream_chunk_delay_seconds > 0:
                        await asyncio.sleep(chat_stream_chunk_delay_seconds)

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


_NIFTY_UI_DIR = Path(__file__).resolve().parent / "static"
if _NIFTY_UI_DIR.is_dir():
    app.mount(
        "/nifty",
        StaticFiles(directory=str(_NIFTY_UI_DIR), html=True),
        name="nifty_chat_ui",
    )

