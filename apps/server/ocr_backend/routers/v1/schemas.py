"""Request-side Pydantic schemas for the OpenAI-compatible v1 API.

Both request AND response types use the `openai` Python library directly.

openai TypedDicts (TypedDict) are used for message params — Pydantic v2 can
validate them natively.  Response types (BaseModel subclasses) come from:
  openai.types.chat.ChatCompletion          – POST /v1/chat/completions (non-stream)
  openai.types.chat.ChatCompletionChunk     – POST /v1/chat/completions (stream)
  openai.types.FileObject                   – POST /v1/files
  openai.types.Model                        – GET  /v1/models
  openai.types.CompletionUsage              – embedded in ChatCompletion
"""

from __future__ import annotations

from typing import Any, List, Literal, Optional

from openai.types.chat import ChatCompletionMessageParam

from openai.types.chat.chat_completion_content_part_text_param import (
    ChatCompletionContentPartTextParam,
)
from pydantic import BaseModel, ConfigDict, model_validator

from openai.types.model import Model
from typing import Iterable
import time

# ---------------------------------------------------------------------------
# Chat request
# ---------------------------------------------------------------------------


class ChatCompletionRequest(BaseModel):
    """
    Uses openai.types.chat.ChatCompletionMessageParam for messages — the exact
    same TypedDict the official openai client uses.

    Example request body
    --------------------
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
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: str = "ocr-v1"
    messages: List[ChatCompletionMessageParam]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    user: Optional[str] = None

    @model_validator(mode="after")
    def require_image_url(self) -> "ChatCompletionRequest":
        if len(self.messages) != 1:
            raise ValueError(f"Exactly one message is required, got {len(self.messages)}.")

        content = self.messages[0].get("content")  # type: ignore[union-attr]

        if not isinstance(content, Iterable):
            raise ValueError("Message content must be a list of content parts.")

        has_text = any(
            isinstance(part, dict)
            and part.get("type") == ChatCompletionContentPartTextParam.__annotations__.get("type", "text")
            or isinstance(part, dict)
            and part.get("type") == "text"
            for part in content
        )
        has_image_or_file = any(
            isinstance(part, dict) and part.get("type") in ("image_url", "file") for part in content
        )

        if not has_text:
            raise ValueError(
                "Message content must include at least one text part (ChatCompletionContentPartTextParam)."
            )
        if not has_image_or_file:
            raise ValueError(
                "Message content must include at least one image_url (ChatCompletionContentPartImageParam) "
                "or file (File) content part."
            )

        return self


# ---------------------------------------------------------------------------
# Models list wrapper  (mirrors the OpenAI list envelope)
# Use openai.types.Model for individual model entries.
# ---------------------------------------------------------------------------


class ModelList(BaseModel):
    """Thin list envelope matching the OpenAI /v1/models response."""

    object: Literal["list"] = "list"
    data: List[Any]  # list[openai.types.Model]


_AVAILABLE_MODELS: list[Model] = [
    Model(id="ocr-v1", created=int(time.time()), object="model", owned_by="ocr-api"),
]
