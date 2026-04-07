import os
import boto3
from openai import AsyncOpenAI
from services.base.pipeline import Pipeline
from business.cache.sql_cache import TaskCache

# Models
from business.checkbox_service.models.morpho import MorphoBoxDetection
from business.paddleocr2.models.paddle import PaddleInferOCR2
from business.llm.models.vision import LLMToForm
from business.llm.models.classification import FormClassification
from business.llm.models.base import VisionLLMOCR
from business.llm.models.template import FormFieldExtractor

# Workers
from business.llm.workers.llm_worker import VLMOcrWorker
from business.forms.workers.pdf_worker import (
    PDFFormsExtractorWorker,
    DefaultPdfExtractor,
)
from business.extractions.worker.file_worker import (
    CSVWorker,
    DocxWorker,
    XlsxWorker,
    OdtWorker,
    OdsWorker,
    OdpWorker,
)
from services.base.worker import AnyFileProcessWorker, DefaultFileProcessWorker

from business.paddleocr2.configs.paddle import PaddleSetting
from src.config.ocr_model import OCRModelSettings

from src.connector import S3Connector, s3_settings

s3_client = boto3.client("s3", verify=s3_settings.VERIFY_SSL)
s3_client_connector = S3Connector(
    s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME
)
main_ocr_settings = OCRModelSettings()


def load_worker(
    name: str,
    batch_size: int = 1,
    worker_weight: float = 1,
) -> Pipeline:
    # logger.info(f"---- {name} selected ----")
    ################# OPENAI CLIENT #################
    openai_client = AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY", "default-api-key"),
        base_url=os.environ.get("OPENAI_API_BASE_URL", "https://api.openai.com/v1"),
    )
    vision_model_name = os.environ.get(
        "VISION_MODEL_NAME", "mistral-small-3.1-24b-instruct-2503"
    )
    #################################################

    ################# CACHE CLIENT ##################
    cache = TaskCache(file_connector=s3_client_connector)
    #################################################

    #################    MODELS   ####################
    ocr_model = PaddleInferOCR2(PaddleSetting().PADDLE_OCR_BASE_DIR)
    morpho_model = MorphoBoxDetection()
    vlm_visual_form_parser = LLMToForm(
        client=openai_client,
        model_name=vision_model_name,
    )
    vlm_visual_ocr_model = VisionLLMOCR(
        client=openai_client, model_name=vision_model_name
    )
    form_visual_classification_model = FormClassification(
        client=openai_client, model_name=vision_model_name
    )
    from_text_field_extractor = FormFieldExtractor(
        client=openai_client, model_name=vision_model_name
    )
    ##################################################

    ################# WORKERS ########################
    default_worker = DefaultFileProcessWorker(
        name="default-worker",
        file_connector=s3_client_connector,
        models=[ocr_model, morpho_model],
        batch_size=2,
        worker_weight=worker_weight,
        cache=cache,
    )
    # Si c'est un pdf and un vrai formulaire (donnée issue de is_form_pdf) on rentre dans ce worker
    # ensuite on prends le texte dans ce pdf, llm -> src.schemas.template.FormEntry
    worker_pdf = PDFFormsExtractorWorker(
        name="pdf-worker-llm-field-extractor",
        file_connector=s3_client_connector,
        models=[from_text_field_extractor],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    default_worker_pdf = DefaultPdfExtractor(
        name="default-pdf-worker",
        file_connector=s3_client_connector,
        models=[],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )

    # On rentre dedans si task.type == TaskOperation.VLM_OCR dans le cas d'un pdf non reconnu formulaire (is_form_pdf=false)
    # on utilise le modèle de VLM pour extraire les informations
    # on classifie le contenu extrait pour savoir si c'est un formulaire
    # on utilise un vlm pour avoir avoir key information extraction

    vlm_ocr_worker = VLMOcrWorker(
        name="vlm-ocr-worker",
        file_connector=s3_client_connector,
        models=[
            vlm_visual_ocr_model,
            form_visual_classification_model,
            vlm_visual_form_parser,
        ],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )

    # On rentre dedans dans les autre cas
    # on classifie le contenu extrait pour savoir si c'est un formulaire
    # on utilise un vlm pour avoir avoir key information extraction
    any_file_worker = AnyFileProcessWorker(
        name="any-file-worker",
        file_connector=s3_client_connector,
        models=[
            ocr_model,
            morpho_model,
            form_visual_classification_model,
            vlm_visual_form_parser,
        ],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )

    ##################################################
    ################# FILE WORKERS ###################
    csv_worker = CSVWorker(
        name="csv-worker",
        file_connector=s3_client_connector,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    xlsx_worker = XlsxWorker(
        name="xlsx-worker",
        file_connector=s3_client_connector,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    docx_worker = DocxWorker(
        name="docx-worker",
        file_connector=s3_client_connector,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    odt_worker = OdtWorker(
        name="odt-worker",
        file_connector=s3_client_connector,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    ods_worker = OdsWorker(
        name="ods-worker",
        file_connector=s3_client_connector,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    odp_worker = OdpWorker(
        name="odp-worker",
        file_connector=s3_client_connector,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=cache,
    )
    ##################################################
    workers = [
        csv_worker,  # TaskOperation.DEFAULT and text/csv
        xlsx_worker,  # TaskOperation.DEFAULT and application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        docx_worker,  # TaskOperation.DEFAULT and application/vnd.openxmlformats-officedocument.wordprocessingml.document
        odt_worker,  # TaskOperation.DEFAULT and application/vnd.oasis.opendocument.text
        ods_worker,  # TaskOperation.DEFAULT and application/vnd.oasis.opendocument.spreadsheet
        odp_worker,  # TaskOperation.DEFAULT and application/vnd.oasis.opendocument.presentation
        default_worker_pdf,  # TaskOperation.DEFAULT and application/pdf AND is_form_pdf
        default_worker,  # TaskOperation.DEFAULT
        worker_pdf,  # application/pdf AND is_form_pdf
        vlm_ocr_worker,  # TaskOperation.VLM_OCR
        any_file_worker,  # OTHER
    ]

    try:
        from business.docling_inference.worker.docling_worker import DoclingWorker
        from business.docling_inference.models.inference import DoclingInferenceModel

        model_docling = DoclingInferenceModel()
        worker_docling = DoclingWorker(
            name="docling-worker",
            file_connector=s3_client_connector,
            models=[model_docling],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )
        workers.insert(3, worker_docling)  # TaskOperation.DOCLING

    except ImportError as e:
        print(e)

    return Pipeline(workers=workers)
