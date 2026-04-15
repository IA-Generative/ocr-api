import torch
import clip
from PIL import Image
from time import time


from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.logger import logger
from src.schemas.classification import ClassificationResult, LabelDefinition, Model
from business.paddleocr2.configs.paddle import PaddleSetting

settings = PaddleSetting()


class OpenAIClipModel(BaseModelPrediction):
    def __init__(self, model_name: str = "ViT-L/14", device: str = "cpu"):
        # Charger modèle
        self.model_name = model_name
        self.device = device
        self.model, self.preprocess = clip.load(model_name, device=device, download_root=settings.CLIP_MODEL_DIR)
        self.model_definition = Model(name=model_name, version="1.0")
        self.labels: list[LabelDefinition] | None = None

    def set_labels(self, labels: list[LabelDefinition]):
        self.labels = labels

    def batch_predict(
        self,
        images: list[Image.Image],
        pages: list = [],
        labels: list[LabelDefinition] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []
        if len(pages):
            assert len(images) == len(pages), "Number of images and pages must match"
        if len(labels):
            self.set_labels(labels)

        # Préparer les labels pour CLIP
        text_features = None
        if self.labels:
            text = clip.tokenize([label.label for label in self.labels]).to(self.device)
            with torch.no_grad():
                text_features = self.model.encode_text(text)
                text_features /= text_features.norm(dim=-1, keepdim=True)
        else:
            logger.warning("No labels provided for classification. Skipping classification step.")
            return pages  # Pas de classification possible sans labels
        if text_features is None:
            return pages  # Pas de classification possible sans labels

        for i, image in enumerate(images):
            t = time()
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                similarities = (image_features @ text_features.T)[0]
                classifications = []
                for j, score in enumerate(similarities):
                    classifications.append(
                        ClassificationResult(
                            label=self.labels[j],
                            confidence=float(score.item()),
                            model=self.model_definition,
                        )
                    )

            pages[i].classifications = classifications
            result.append(pages[i])
            logger.info(f"[CLIP] Inference time: {time() - t:.2f}s")
        return result
