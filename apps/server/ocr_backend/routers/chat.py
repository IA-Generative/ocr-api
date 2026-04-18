import logging
from typing import List, Literal, Optional, Annotated, AsyncGenerator


import instructor
from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ocr_backend.core.security.factory import TokenVerifier
from ocr_backend.core.security.token import RequestContext
from src.config.openai import OpenAISettings
from src.models.ocr_chunks import OcrChunkSearchResult, ocr_chunk_repo
from src.services.task_service import TaskService
from src.schemas.task import TaskOperation
from src.connector.db_connector import AsyncSessionLocal


TokenDep = Annotated[RequestContext, Depends(TokenVerifier)]
TaskServiceDep = Annotated[TaskService, Depends(TaskService)]


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]

router = APIRouter(tags=["Chat"])

_openai_settings = OpenAISettings()
_client = AsyncOpenAI(
    api_key=_openai_settings.OPENAI_API_KEY,
    base_url=_openai_settings.OPENAI_BASE_URL,
)
_instructor_client = instructor.from_openai(_client)

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


class StructuredReply(BaseModel):
    """Structured LLM response with source attribution."""

    content: str = Field(description="La réponse à la question de l'utilisateur")
    used_sources: List[int] = Field(
        default_factory=list,
        description="Indices (0-based) des sources effectivement utilisées pour formuler la réponse. Liste vide si aucune source n'est pertinente.",
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
    ctx: TokenDep,
    task_service: TaskServiceDep,
    db_session: DbSessionDep,
):
    """Submit a list of messages and receive the assistant's reply.

    When ``content_hash`` and ``query_vector`` are provided, the top-K most
    relevant OCR chunks are retrieved via cosine similarity and injected as a
    system message before the conversation.  The matched chunks are returned in
    ``sources`` so the client can highlight the corresponding bboxes.

    No conversation history is stored server-side.
    """
    task = await task_service.get_task_by_id(task_id=body.task_id, db=db_session, task_type=TaskOperation.OCR)
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
            context_text = "\n\n".join(
                f"[Source {i}] (Pages {s.page_nums}, bboxes {s.bbox_indices})\n{s.text}" for i, s in enumerate(sources)
            )
            context_msg = {
                "role": "system",
                "content": (
                    "Voici des extraits du document OCR. Chaque extrait est identifié par un numéro de source.\n"
                    "Utilise uniquement les extraits pertinents pour répondre.\n"
                    "Dans used_sources, indique les indices des sources que tu as utilisées.\n\n" + context_text
                ),
            }
            # Insert context right before the first user message
            first_user = next((i for i, m in enumerate(messages) if m["role"] == "user"), 0)
            messages.insert(first_user, context_msg)
    try:
        structured_reply: StructuredReply = await _instructor_client.chat.completions.create(
            model=body.model,
            messages=messages,
            response_model=StructuredReply,
        )
        reply_content = structured_reply.content
        used_indices = [i for i in structured_reply.used_sources if isinstance(i, int) and 0 <= i < len(sources)]
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return AskResponse(
            message=ChatMessage(
                role="assistant",
                content=f"Error generating response: {str(e)}",
            ),
            sources=[],
        )

    filtered_sources = [sources[i] for i in used_indices]

    return AskResponse(
        message=ChatMessage(role="assistant", content=reply_content),
        sources=[
            UsedChunk(
                page_nums=s.page_nums,
                bbox_indices=s.bbox_indices,
                text=s.text,
            )
            for s in filtered_sources
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
    ctx: TokenDep,
):
    res = await _client.embeddings.create(
        input=body.text,
        model=_openai_settings.EMBEDDINGS_MODEL,
    )
    return EmbedResponse(vector=res.data[0].embedding, model=_openai_settings.EMBEDDINGS_MODEL)
