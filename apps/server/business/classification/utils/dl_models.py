import clip
from src.logger import setup_logger

logger = setup_logger("classification_utils")


def download_clip_model(model_name: str = "ViT-L/14", device: str = "cpu"):
    """Télécharge le modèle CLIP spécifié et son préprocesseur associé."""
    model, preprocess = clip.load(model_name, device=device)
    return model, preprocess


if __name__ == "__main__":
    # Exemple d'utilisation
    model_name = "ViT-L/14"
    device = "cpu"
    model, preprocess = download_clip_model(model_name, device)
    logger.info(f"Modèle {model_name} téléchargé avec succès sur {device}.")
