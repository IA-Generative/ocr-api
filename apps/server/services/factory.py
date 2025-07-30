import os
import boto3

from services.base.worker import AnyFileProcessWorker
from services.base.pipeline import Pipeline
from business.forms.workers.pdf_worker import PDFFormsExtractorWorker
from business.cache.sql_cache import TaskCache
from business.checkbox_service.models.morpho import MorphoBoxDetection
from src.config.ocr_model import OCRModelSettings

from src.connector import S3Connector, s3_settings
from src.logger import logger

s3_client = boto3.client("s3")
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)
main_ocr_settings = OCRModelSettings()

DEVICE = os.environ.get("DEVICE", "cpu")


def load_worker(name: str, batch_size: int = 1, worker_weight: float = 1) -> Pipeline:
    logger.info(f"---- {name} selected ----")
    models = []
    model = None
    if name == "paddleocr-2.10.0":
        from business.paddleocr2.models.paddle import PaddleInferOCR2
        from business.paddleocr2.configs.paddle import PaddleSetting

        model = PaddleInferOCR2(PaddleSetting().PADDLE_OCR_BASE_DIR)
        models.append(model)

    elif name == "paddleocr-3.0.1":
        from business.paddleocr3.config import PaddleSetting
        from business.paddleocr3.models.paddle_pipe import PaddleInferOCR

        ocr_settings = PaddleSetting()

        model = PaddleInferOCR(
            device=DEVICE,
            batch_size=ocr_settings.DETECTION_BATCH_SIZE,
            ocr_version=ocr_settings.OCR_VERSION,
            lang=ocr_settings.OCR_LANG,
            text_detection_model_name=f"{ocr_settings.OCR_VERSION}_mobile_det",
            text_recognition_model_name=f"{ocr_settings.OCR_VERSION}_mobile_rec",
        )
        models.append(model)

    elif name == "paddleocr-3.0.1-pipeline":
        from business.paddleocr3.config import PaddleSetting
        from business.paddleocr3.models.paddle_pipe import PaddleInferOCR

        ocr_settings = PaddleSetting()
        ocr_model = PaddleInferOCR(
            device=DEVICE,
            batch_size=ocr_settings.DETECTION_BATCH_SIZE,
            ocr_version=ocr_settings.OCR_VERSION,
            lang=ocr_settings.OCR_LANG,
        )
        models.append(ocr_model)
        if ocr_settings.USE_LAYOUT_DETECTION:
            from business.paddleocr3.models.layout import PaddleLayoutDetection

            models.append(PaddleLayoutDetection(device=DEVICE))
            if ocr_settings.USE_FORMULA_RECOGNITION:
                from business.paddleocr3.models.formula import PaddleFormulaRecognizer

                models.append(PaddleFormulaRecognizer(device=DEVICE))

            if ocr_settings.USE_TABLE_RECOGNITION:
                from business.paddleocr3.models.table import TablePrediction

                models.append(TablePrediction(device=DEVICE))

        # model = PipelineLinearPrediction(models=tmp_models)
        # models.append(model)

    elif name == "only-llm":
        from openai import OpenAI
        from business.llm.models.base import VisionLLMOCR
        from business.llm.models.template import TemplateLLMDetector
        from business.llm.config import OpenAISetting

        openai_settings = OpenAISetting()
        client = OpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            base_url=openai_settings.OPENAI_BASE_URL,
        )

        models.append(VisionLLMOCR(client=client, model_name=openai_settings.VISION_MODEL))
        models.append(TemplateLLMDetector(client=client, model_name=openai_settings.INSTRUCT_MODEL_NAME))

    elif name == "mixed-classic-and-vlm":
        from openai import OpenAI
        from business.llm.models.template import TemplateLLMDetector
        from business.llm.config import OpenAISetting

        openai_settings = OpenAISetting()
        client = OpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            base_url=openai_settings.OPENAI_BASE_URL,
        )
        base_worker = load_worker(
            name="paddleocr-3.0.1-pipeline",
            batch_size=batch_size,
            worker_weight=worker_weight,
        )
        base_worker.models.append(TemplateLLMDetector(client=client, model_name=openai_settings.INSTRUCT_MODEL_NAME))
        return base_worker

    else:
        raise NotImplementedError("")

    if main_ocr_settings.USE_VISION_LLM_EXTRACT_KIE:
        from openai import AsyncOpenAI
        from business.llm.config import OpenAISetting

        openai_settings = OpenAISetting()
        client = AsyncOpenAI(
            api_key=openai_settings.OPENAI_API_KEY,
            base_url=openai_settings.OPENAI_BASE_URL,
        )
        from business.llm.models.vision import LLMToForm

        models.append(LLMToForm(client=client, model_name=openai_settings.VISION_MODEL))

    models.append(MorphoBoxDetection())

    next_worker = AnyFileProcessWorker(
        name=name,
        file_connector=s3_client_connector,
        models=models,
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=TaskCache(file_connector=s3_client_connector),
    )
    worker_pdf = PDFFormsExtractorWorker(
        name=f"pdf-{name}",
        file_connector=s3_client_connector,
        models=[],
        batch_size=batch_size,
        worker_weight=worker_weight,
        cache=TaskCache(file_connector=s3_client_connector),
    )

    return Pipeline(workers=[worker_pdf, next_worker])
