import json
from typing import AsyncGenerator, Any


async def events_to_sse_tokens(events: Any) -> AsyncGenerator[str, None]:
    """Convert LangGraph astream_events output to SSE token strings."""
    async for event in events:
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
