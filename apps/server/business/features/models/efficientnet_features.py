from efficientnet_pytorch import EfficientNet
from PIL import Image
import torch
from torchvision import transforms

from business.features.models.features_extraction import FeatureCreator


class EfficientImageFeatureExtractor(FeatureCreator):
    """Extracteur de features pour images utilisant EfficientNet"""

    def __init__(self, model_name: str = "efficientnet-b0"):
        """
        Initialise l'extracteur de features

        Args:
            model_name: Nom du modèle EfficientNet à utiliser
        """
        print(f"Chargement du modèle {model_name}...")
        self.model = EfficientNet.from_pretrained(model_name)
        self.model.eval()

        # Transformations d'image standardisées
        self.transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
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
        image = image.convert("RGB")
        input_tensor = self.transform(image).unsqueeze(0)

        # Extraire les features
        with torch.no_grad():
            features = self.model.extract_features(input_tensor)

        # Réduction de dimension (moyenne globale)
        features = features.mean(dim=[2, 3]).squeeze().cpu().numpy().tolist()
        return features

    def get_feature_size(self) -> int:
        """
        Retourne la taille du vecteur de features

        Returns:
            Taille du vecteur de features
        """
        return self.model_size
