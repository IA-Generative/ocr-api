import json
from io import BytesIO

from docling.datamodel.base_models import ConversionStatus, DocumentStream, InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)
from docling.document_converter import (
    DocumentConverter,
    ImageFormatOption,
    PdfFormatOption,
)
from docling_core.types.doc.document import DoclingDocument
from PIL import Image

from ocr_service.models.base import BaseModelPrediction
from src.schemas.output import MarkdownPage


def image2stream(image, format="PNG"):
    buf = BytesIO()
    image.save(buf, format=format)
    buf.seek(0)
    return buf


class DoclingInferOCR(BaseModelPrediction):
    def __init__(self):
        # https://docling-project.github.io/docling/reference/pipeline_options/#docling.datamodel.pipeline_options.PdfPipelineOptions
        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
            do_code_enrichment=True,
            do_picture_description=False,
            do_ocr=True,
        )
        # ocr_options= RapidOcrOptions(lang=["english", "french"]))

        self.doc_converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.IMAGE,
                InputFormat.DOCX,
                InputFormat.HTML,
                InputFormat.PPTX,
            ],
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                ),  # backend=PdfBackend.DLPARSE_V4
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            },
        )

    def batch_predict(
        self, images: list[Image.Image | BytesIO], *args, **kwargs
    ) -> list[MarkdownPage]:
        result: list[DoclingDocument] = []

        list_documentstream: list[DocumentStream] = [
            DocumentStream(name="image.png", stream=image2stream(image_or_buffer))
            if isinstance(image_or_buffer, Image.Image)
            else DocumentStream(name="doc.pdf", stream=image_or_buffer)
            for image_or_buffer in images
        ]

        conv_results = self.doc_converter.convert_all(
            list_documentstream,
            raises_on_error=True,  # whether let conversion run through all and examine results at the end
        )

        for i, conversion_result in enumerate(conv_results):
            assert conversion_result.status == ConversionStatus.SUCCESS
            result.append(
                MarkdownPage(
                    page=i,
                    doc_json=json.dumps(conversion_result.export_to_dict()),
                    markdown=conversion_result.document.export_to_markdown(),
                )
            )

        return result
