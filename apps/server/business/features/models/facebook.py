from PIL import Image
from transformers import AutoImageProcessor, AutoModel
import torch

from business.features.models.features_extraction import FeatureCreator


class FacebookImageFeatureExtractor(FeatureCreator):
    """Extracteur de features pour images utilisant les modèles Facebook"""

    def __init__(self, model_name: str = "facebook/dinov2-small"):
        """
        Initialise l'extracteur de features

        Args:
            model_name: Nom du modèle Facebook à utiliser
        """
        print(f"Chargement du modèle {model_name}...")
        self.model = AutoModel.from_pretrained(model_name)
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model.eval()
        self.model_name = model_name

        # Test pour déterminer la taille de sortie
        warmup_image = Image.new("RGB", (224, 224))
        test_features = self.get_vector_from_image(warmup_image)
        self.model_size = len(test_features)
        print(f"Taille des features: {self.model_size}")

    def get_vector_from_image(self, image: Image.Image) -> list[float]:
        """
        Extrait les features d'une image

        Args:
            image: Image à traiter

        Returns:
            Vecteur de features de l'image
        """
        inputs = self.processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Pour DINOv2, utiliser le token CLS (premier token) comme représentation globale
        # last_hidden_states shape: [batch_size, sequence_length, hidden_size]
        last_hidden_states = outputs.last_hidden_state

        # Extraire le token CLS (index 0) qui contient la représentation globale de l'image
        cls_token = last_hidden_states[0, 0, :]  # [hidden_size]

        return cls_token.cpu().numpy().tolist()

    def get_feature_size(self) -> int:
        """
        Retourne la taille du vecteur de features

        Returns:
            Taille du vecteur de features
        """
        return self.model_size
