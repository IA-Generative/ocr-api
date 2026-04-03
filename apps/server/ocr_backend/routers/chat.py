import logging
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from ocr_backend.core.security.factory import TokenVerifier
from ocr_backend.core.security.token import RequestContext
from src.config.openai import OpenAISettings
from src.schemas.ocr_chunks import OcrChunkSearchResult, ocr_chunk_repo
from src.schemas.task import task_table

router = APIRouter(tags=["Chat"])

_openai_settings = OpenAISettings()
_client = AsyncOpenAI(
    api_key=_openai_settings.OPENAI_API_KEY,
    base_url=_openai_settings.OPENAI_BASE_URL,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class UsedChunk(BaseModel):
    page_nums: List[int]
    bbox_indices: List[int]
    text: str


class AskRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = _openai_settings.OPENAI_MODEL
    task_id: str = Field(..., description="Task ID used to retrieve the document context")
    query_vector: Optional[List[float]] = Field(
        default=None,
        description="Embedding of the last user message, used for semantic chunk retrieval",
    )
    top_k: int = Field(default=5, ge=1, le=20)


class AskResponse(BaseModel):
    message: ChatMessage
    sources: List[UsedChunk] = Field(
        default_factory=list,
        description="OCR chunks injected as context, with their page numbers and bbox indices",
    )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.post(
    "/chat/ask",
    response_model=AskResponse,
    summary="Send a conversation to the LLM and get a single reply (stateless)",
)
async def ask(
    body: AskRequest,
    ctx: RequestContext = Depends(TokenVerifier),
):
    """Submit a list of messages and receive the assistant's reply.

    When ``content_hash`` and ``query_vector`` are provided, the top-K most
    relevant OCR chunks are retrieved via cosine similarity and injected as a
    system message before the conversation.  The matched chunks are returned in
    ``sources`` so the client can highlight the corresponding bboxes.

    No conversation history is stored server-side.
    """
    task = task_table.get_task_by_id(task_id=body.task_id)
    if not task or task.user_id != ctx.user_id:
        return AskResponse(
            message=ChatMessage(
                role="assistant",
                content="Le contexte du document n'est pas disponible. Veuillez réessayer dans quelques instants.",
            ),
            sources=[],
        )
    content_hash = task.content_hash
    sources: List[OcrChunkSearchResult] = []
    messages = [m.model_dump() for m in body.messages]

    if content_hash and body.query_vector:
        sources = ocr_chunk_repo.search(
            content_hash=content_hash,
            query_vector=body.query_vector,
            top_k=body.top_k,
        )
        logger.info(f"Retrieved {len(sources)} relevant chunks for task {body.task_id} (content hash {content_hash})")
        logger.info(
            f"Sources: {[{'page_nums': s.page_nums, 'bbox_indices': s.bbox_indices, 'text': s.text[:50]} for s in sources]}"
        )
        if sources:
            context_text = "\n\n".join(f"[Pages {s.page_nums}, bboxes {s.bbox_indices}]\n{s.text}" for s in sources)
            context_msg = {
                "role": "system",
                "content": (
                    "Voici des extraits du document OCR pertinents pour répondre à la question :\n\n" + context_text
                ),
            }
            # Insert context right before the first user message
            first_user = next((i for i, m in enumerate(messages) if m["role"] == "user"), 0)
            messages.insert(first_user, context_msg)
    try:
        completion = await _client.chat.completions.create(
            model=body.model,
            messages=messages,
        )
        reply = completion.choices[0].message
    except Exception as e:
        reply = ChatMessage(role="assistant", content=f"Error generating response: {str(e)}")
        return AskResponse(message=reply, sources=[])
    return AskResponse(
        message=ChatMessage(role=reply.role, content=reply.content or ""),
        sources=[
            UsedChunk(
                page_nums=s.page_nums,
                bbox_indices=s.bbox_indices,
                text=s.text,
            )
            for s in sources
        ],
    )


# ---------------------------------------------------------------------------
# Embed endpoint — returns the embedding vector for a query string
# ---------------------------------------------------------------------------


class EmbedRequest(BaseModel):
    text: str = Field(..., description="Text to embed")


class EmbedResponse(BaseModel):
    vector: List[float]
    model: str


@router.post(
    "/chat/embed",
    response_model=EmbedResponse,
    summary="Return the embedding vector for a text query",
)
async def embed(
    body: EmbedRequest,
    ctx: RequestContext = Depends(TokenVerifier),
):
    res = await _client.embeddings.create(
        input=body.text,
        model=_openai_settings.EMBEDDINGS_MODEL,
    )
    return EmbedResponse(vector=res.data[0].embedding, model=_openai_settings.EMBEDDINGS_MODEL)
