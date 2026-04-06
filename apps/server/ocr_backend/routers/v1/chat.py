"""POST /v1/chat/completions — OpenAI-compatible chat completions with OCR support."""

import asyncio
import time
from typing import AsyncGenerator, Union, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice, ChoiceDelta

from ocr_backend.core.security.factory import ApiToken
from ocr_backend.core.security.token import RequestContext

from .schemas import ChatCompletionRequest, _AVAILABLE_MODELS
from .utils import (
    get_latest_task_status,
    retrieve_file_or_image_from_chat_message,
    sending_file_to_ocr_service,
)
import json

router = APIRouter(tags=["Chat"], prefix="/chat")

_TERMINAL_SUCCESS = {"done", "success"}
_TERMINAL_ERROR = {"failed", "error"}


def _build_completion(model: str, content: str, completion_id: str) -> ChatCompletion:
    """Build an openai.types.chat.ChatCompletion response object."""
    return ChatCompletion(
        id=completion_id,
        object="chat.completion",
        created=int(time.time()),
        model=model,
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    content=content,
                    refusal=None,
                ),
                finish_reason="stop",
                logprobs=None,
            )
        ],
        usage=CompletionUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        ),
    )


# ---------------------------------------------------------------------------
# Streaming generator
# ---------------------------------------------------------------------------


async def _stream_response(
    model: str,
    task_id: str,
    poll_interval: float = 1.0,
) -> AsyncGenerator[str, None]:
    """Poll the task until terminal state, then stream the OCR text word by word."""

    created = int(time.time())

    def _chunk(
        delta: ChoiceDelta,
        finish_reason: (Literal["stop", "length", "tool_calls", "content_filter", "function_call"] | None) = None,
    ) -> str:
        chunk = ChatCompletionChunk(
            id=task_id,
            object="chat.completion.chunk",
            created=created,
            model=model,
            choices=[
                ChunkChoice(
                    index=0,
                    delta=delta,
                    finish_reason=finish_reason,
                    logprobs=None,
                )
            ],
        )
        return f"data: {chunk.model_dump_json()}\n\n"

    yield _chunk(ChoiceDelta(role="assistant"))

    # Poll until the task reaches a terminal state
    while True:
        task = get_latest_task_status(task_id)  # raises HTTP 404 if task deleted
        status = task.get("status", "")

        if status in _TERMINAL_SUCCESS:
            break

        if status in _TERMINAL_ERROR:
            yield _chunk(ChoiceDelta(content=json.dumps(task)), finish_reason="stop")
            yield "data: [DONE]\n\n"
            return

        await asyncio.sleep(poll_interval)

    # Stream OCR text word by word
    output = task.get("output") or {}
    text: str = (output.get("text") or "").strip()
    words = text.split()
    for word in words:
        yield _chunk(ChoiceDelta(content=word + " "))
        await asyncio.sleep(0)

    yield _chunk(ChoiceDelta(), finish_reason="stop")
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.post(
    "/completions",
    summary="Create a chat completion (OCR)",
    response_model=ChatCompletion,
)
async def chat_completions(
    request: ChatCompletionRequest,
    ctx: RequestContext = Depends(ApiToken()),
) -> Union[ChatCompletion, StreamingResponse]:
    """
    Example request
    ---------------
    POST /v1/chat/completions
    Authorization: Bearer <token>
    {
        "model": "ocr-v1",
        "stream": false,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this image."},
                    {"type": "image_url", "image_url": {"url": "https://example.com/doc.png"}}
                ]
            }
        ]
    }
    or
    {
        "model": "ocr-v1",
        "stream": false,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this image."},
                    {"type": "file", "file": {"file_data": "https://example.com/doc.png", "filename": "doc.png", "file_id": "file-abc123"}}
                ]
            }
        ]
    }


    When stream=true the response is a text/event-stream of ChatCompletionChunk objects.
    When stream=false processing runs in the background; poll GET /v1/tasks/{task_id}.
    """

    if request.model not in [model.id for model in _AVAILABLE_MODELS]:
        raise HTTPException(status_code=400, detail=f"Unsupported model {request.model}")

    file_path = retrieve_file_or_image_from_chat_message(request)  # raises 422 if no valid image/file found
    task = sending_file_to_ocr_service(
        user_id=ctx.user_id,  # type: ignore
        group_id=ctx.groups[0] if ctx.groups else "DEFAULT",  # type: ignore
        task_operation="ocr",
        file_path=file_path,
    )
    if file_path.exists():
        file_path.unlink()

    task_id = task["id"]

    if request.stream:
        return StreamingResponse(
            _stream_response(model=request.model, task_id=task_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Return immediately; client should poll GET /v1/tasks/{task_id} for the result.
    return _build_completion(
        model=request.model,
        content=json.dumps(task),
        completion_id=task_id,
    )
