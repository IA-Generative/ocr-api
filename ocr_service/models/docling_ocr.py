import json
from collections import defaultdict
from io import BytesIO

from docling.datamodel.base_models import ConversionStatus, DocumentStream, InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
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
from src.schemas.box import Bbox
from src.schemas.output import DoclingDocument, DoclingPage, MarkdownPageWithBBox


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
            generate_page_images=True,
            ocr_options=EasyOcrOptions(force_full_page_ocr=True, lang=["en", "fr"]),
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
                ),  # backend=DoclingParseV4DocumentBackend from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            },
        )

    def batch_predict(
        self, images_or_bytes_io: list[Image.Image | BytesIO], *args, **kwargs
    ) -> list[DoclingDocument] | list[MarkdownPageWithBBox]:
        result: list = []

        # Si on a une liste d'images, on est en mode PADDLE on retourne les bbox
        # Sinon on retourne un objet Document de plusieurs pages
        output_iso_paddle = all(isinstance(Image.Image, image_or_byte_io) for image_or_byte_io in images_or_bytes_io)

        list_documentstream: list[DocumentStream] = [
            DocumentStream(name="image.png", stream=image2stream(image_or_buffer))
            if isinstance(image_or_buffer, Image.Image)
            else DocumentStream(name="doc.pdf", stream=image_or_buffer)
            for image_or_buffer in images_or_bytes_io
        ]

        conv_results = self.doc_converter.convert_all(
            list_documentstream,
            raises_on_error=True,  # whether let conversion run through all and examine results at the end
        )

        for i, conversion_result in enumerate(conv_results):
            assert conversion_result.status == ConversionStatus.SUCCESS

            boxes: list[Bbox] = []
            boxes_with_pages = defaultdict(list)  # dico page_no:int => boxes: list[Bbox]

            for text in conversion_result.document.texts:
                assert not (output_iso_paddle) or len(conversion_result.document.pages) == 1
                provenance_item = text.prov[0]
                page_item = conversion_result.document.pages[provenance_item.page_no]
                page_height = page_item.size.height
                page_width = page_item.size.width
                cbbox = provenance_item.bbox.to_top_left_origin(page_height=page_height)
                text_region = [[cbbox.l, cbbox.t], [cbbox.r, cbbox.b], [cbbox.r, cbbox.b], [cbbox.l, cbbox.b]]

                x_coords = [point[0] for point in text_region]
                y_coords = [point[1] for point in text_region]
                x = min(x_coords)
                y = min(y_coords)
                w = max(x_coords) - x
                h = max(y_coords) - y

                # Normalize coordinates between 0 and 1
                norm_x = x / page_width
                norm_y = y / page_height
                norm_w = w / page_width
                norm_h = h / page_height

                box = Bbox(
                    x=norm_x,
                    y=norm_y,
                    width=norm_w,
                    height=norm_h,
                    confidence=float(1.0),  # TODO
                    text=text.text,
                )

                boxes.append(box)
                boxes_with_pages[provenance_item.page_no].append(box)

            pages: list[DoclingPage] = [
                DoclingPage(page_no=page_no, boxes=boxes_with_pages[page_no], pil_image=page_item.image.pil_image)
                for page_no, page_item in conversion_result.document.pages.items()
            ]  # attention page_no commence à 1

            if output_iso_paddle:
                result.append(
                    MarkdownPageWithBBox(
                        page=i,
                        doc_json=json.dumps(conversion_result.document.export_to_dict()),
                        markdown=conversion_result.document.export_to_markdown(),
                        boxes=boxes,
                    )
                )
            else:
                result.append(
                    DoclingDocument(
                        doc_json=json.dumps(conversion_result.document.export_to_dict()),
                        markdown=conversion_result.document.export_to_markdown(),
                        pages=pages,
                    )
                )

        assert len(result) == len(images_or_bytes_io)

        return result
