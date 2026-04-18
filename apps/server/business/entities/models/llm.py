import openai
from pydantic import BaseModel, Field
from src.schemas.task import TaskModel
from src.schemas.classification import Model
from business.chunks.models.chunker import OcrChunker
from src.schemas.box import Bbox
from src.schemas.output import Page
from src.schemas.entity import (
    EntityPrediction,
    EntityExtractionResult,
    ParameterEntityDefinition,
)
from src.schemas.ocr_chunks import OcrChunkSearchResult

from services.client.tools import server_client
from src.config.openai import OpenAISettings
import instructor


class _ChunkMatch(BaseModel):
    chunk_id: int = Field(description="The numeric ID of the matching chunk")
    value: str | None = Field(default=None, description="The exact extracted value from the chunk text")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that this chunk matches the entity definition",
    )


class _LLMEntityOutput(BaseModel):
    matches: list[_ChunkMatch] = Field(
        default_factory=list,
        description="List of chunk IDs that match the entity definition",
    )


settings = OpenAISettings()


class TextEntityExtractionModel:
    def __init__(
        self,
        client: openai.OpenAI = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL),
        model_name: str = settings.OPENAI_MODEL,
    ):
        # Charger modèle
        self.model_name = model_name
        self.model_definition = Model(name=model_name, version="1.0")
        self.client = client
        self.prompt = (
            "You are a document entity extraction assistant.\n\n"
            "You are given:\n"
            "1. An ENTITY DEFINITION describing the entity to find.\n"
            "2. A list of TEXT CHUNKS extracted from a document, each identified by a numeric ID. "
            "These chunks have been pre-selected as semantically close to the entity definition.\n\n"
            "Your task:\n"
            "- Read each chunk carefully.\n"
            "- Select the IDs of the chunks that actually contain or express the entity described in the definition.\n"
            "- A chunk should be selected only if it genuinely matches the entity, not just because it is topically related.\n"
            "- For each selected chunk, extract the exact value of the entity as it appears in the text (if applicable).\n\n"
            "ENTITY DEFINITION:\n"
            "{entity_definition}\n"
            "{chunks}\n\n"
            "Return only the chunk IDs that match, with the extracted value for each."
        )
        self.client_instructor = instructor.from_openai(client, mode=instructor.Mode.MD_JSON)
        self.chunker = OcrChunker()

    def get_corresonding_bbox(self, chunk: OcrChunkSearchResult, pages: list[Page]) -> list[Bbox]:
        bboxes = []
        for page_num in chunk.page_nums:
            page = next((p for p in pages if p.page == page_num), None)
            if page is None:
                continue
            for bbox_index in chunk.bbox_indices:
                if bbox_index < 0 or bbox_index >= len(page.boxes):
                    continue
                bbox = page.boxes[bbox_index]
                if bbox is not None:
                    bboxes.append(bbox)
        return bboxes

    def process(self, task: TaskModel) -> EntityExtractionResult:
        if task.input is None or task.parameters is None or task.content_hash is None:
            raise ValueError("Task input, parameters, and content hash are required for entity extraction")

        parameter_entity_definition = ParameterEntityDefinition.model_validate(task.parameters)
        if not parameter_entity_definition.entities_definitions:
            raise ValueError("At least one entity definition is required for extraction")
        if task.output is None or not hasattr(task.output, "pages"):
            raise ValueError("Task output with 'pages' attribute is required for extraction")
        pages = task.output.pages

        all_predictions: list[EntityPrediction] = []

        for definition in parameter_entity_definition.entities_definitions:
            definition_str = definition.model_dump_json(exclude_unset=True)

            query_vector = self.chunker.embed_text(texts=[definition_str])

            search_result: list[dict] = server_client.search_chunks(
                content_hash=task.content_hash,
                query_vector=query_vector[0],
                top_k=None,
                threshold=0.5,
            )
            search_result_models = [OcrChunkSearchResult.model_validate(r) for r in search_result]
            if not search_result_models:
                continue

            simple_id_mapper = dict(enumerate(search_result_models))

            chunks_str = "\n\n".join(
                f"[ID {i}] (similarity: {c.score:.2f})\n{c.text}" for i, c in simple_id_mapper.items()
            )

            filled_prompt = self.prompt.format(
                entity_definition=definition_str,
                chunks=chunks_str,
            )

            llm_output: _LLMEntityOutput = self.client_instructor.chat.completions.create(
                model=self.model_name,
                response_model=_LLMEntityOutput,
                messages=[{"role": "user", "content": filled_prompt}],
            )

            for match in llm_output.matches:
                chunk = simple_id_mapper.get(match.chunk_id)
                if chunk is None:
                    continue
                all_predictions.append(
                    EntityPrediction(
                        entity_name=definition.name,
                        confidence=match.confidence,
                        value=match.value,
                        bbox=self.get_corresonding_bbox(chunk, pages),
                        pages=chunk.page_nums,
                    )
                )

        return EntityExtractionResult(entities=all_predictions)
