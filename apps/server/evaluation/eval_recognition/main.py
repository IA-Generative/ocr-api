import os
import uuid
import argparse
from langfuse import Langfuse

from evaluation.eval_recognition.data import PixParseDataset
from evaluation.eval_recognition.core_evaluation import Evaluation


DATASET_CLASSES = {"pixparse": PixParseDataset}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR Evaluation")
    parser.add_argument(
        "--model",
        choices=["paddle", "vlm", "docling"],
        required=True,
        help="Choisir le modèle à évaluer : 'paddle' ou 'vlm'",
        default="paddle",
    )
    parser.add_argument(
        "--dataset",
        choices=list(DATASET_CLASSES.keys()),
        required=True,
        help="Choisir le dataset à utiliser",
        default="pixparse",
    )
    args = parser.parse_args()

    langfuse_client = Langfuse(
        secret_key=os.environ.get("LANGFUSE_SECRET_KEY", "sk-lf-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"),
        public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", "pk-lf-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"),
        host=os.environ.get("LANGFUSE_HOST", "http://localhost:3000"),
    )

    dataset_class = DATASET_CLASSES[args.dataset]
    dataset = dataset_class(split="train", langfuse=langfuse_client)

    if args.model == "paddle":
        from business.paddleocr2.models.paddle import PaddleInferOCR2
        from evaluation.eval_recognition.utils import download_model

        download_model("dataset/paddleocr2", version="PP-OCRv4")
        model = PaddleInferOCR2(path_model="dataset/paddleocr2")
        run_name = f"paddle-ocr-evaluation-{uuid.uuid4()}"
    elif args.model == "vlm":
        from business.llm.models.base import VisionLLMOCR
        from openai import OpenAI

        model = VisionLLMOCR(
            client=OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
                base_url=os.environ.get("OPENAI_API_BASE"),
            ),
            model_name=os.environ.get("OPENAI_API_MODEL", "gpt-4-vision-preview"),
        )
        run_name = f"vlm-evaluation-{uuid.uuid4()}"

    elif args.model == "docling":
        from apps.server.business.docling_inference.models.inference import (
            DoclingInferenceModel,
        )

        model = DoclingInferenceModel()
        run_name = f"docling-evaluation-{uuid.uuid4()}"

    else:
        raise ValueError(f"Modèle inconnu : {args.model}")

    evaluation = Evaluation(
        model=model,
        dataset=dataset,
        langfuse=langfuse_client,
        run_name=run_name,
    )
    evaluation.process()
