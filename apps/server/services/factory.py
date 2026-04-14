import boto3
from openai import AsyncOpenAI
from services.base.pipeline import Pipeline
from business.cache.sql_cache import TaskCache

# Models
from business.paddleocr2.models.paddle import PaddleInferOCR2
from business.llm.models.template import FormFieldExtractor

# Workers
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
from src.config.openai import OpenAISettings

s3_client = boto3.client("s3", verify=s3_settings.VERIFY_SSL)
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)
main_ocr_settings = OCRModelSettings()
openai_settings = OpenAISettings()


def load_worker(
    batch_size: int = 1,
    worker_weight: float = 1,
) -> Pipeline:
    # logger.info(f"---- {name} selected ----")
    ################# OPENAI CLIENT #################
    openai_client = AsyncOpenAI(
        api_key=openai_settings.OPENAI_API_KEY,
        base_url=openai_settings.OPENAI_BASE_URL,
    )
    vision_model_name = openai_settings.OPENAI_MODEL
    #################################################

    ################# CACHE CLIENT ##################
    cache = TaskCache(file_connector=s3_client_connector)
    #################################################

    #################    MODELS   ####################
    ocr_model = PaddleInferOCR2(PaddleSetting().PADDLE_PDX_CACHE_HOME)
    from_text_field_extractor = FormFieldExtractor(client=openai_client, model_name=vision_model_name)
    ##################################################

    ################# WORKERS ########################
    default_worker = DefaultFileProcessWorker(
        name="default-worker",
        file_connector=s3_client_connector,
        models=[ocr_model],
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

    # On rentre dedans dans les autre cas
    # on classifie le contenu extrait pour savoir si c'est un formulaire
    # on utilise un vlm pour avoir avoir key information extraction
    any_file_worker = AnyFileProcessWorker(
        name="any-file-worker",
        file_connector=s3_client_connector,
        models=[ocr_model],
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
        any_file_worker,  # OTHER
    ]

    return Pipeline(workers=workers)  # ty:ignore[invalid-argument-type]
