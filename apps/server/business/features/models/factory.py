import json
import os
from business.features.models.features_extraction import FeatureCreator


def get_feature_extractor(model_name: str) -> FeatureCreator:
    if model_name.startswith("facebook"):
        from business.features.models.facebook import FacebookImageFeatureExtractor

        return FacebookImageFeatureExtractor(model_name=model_name)

    elif model_name.startswith("efficientnet"):
        from business.features.models.efficientnet_features import (
            EfficientImageFeatureExtractor,
        )

        return EfficientImageFeatureExtractor(model_name=model_name)
    elif model_name.startswith("google"):
        from business.features.models.google import GoogleImageFeatureExtractor

        return GoogleImageFeatureExtractor(model_name=model_name)
    elif model_name.startswith("dummy"):
        from business.features.models.features_extraction import DummyFeatureCreator

        return DummyFeatureCreator(model_name=model_name)

    else:
        raise ValueError(f"Unknown model name: {model_name}")


def get_available_feature_extractors(config_dir: str = "configs") -> dict:
    with open(os.path.join(config_dir, "available_feature_extractors.json"), "r") as f:
        return json.load(f)


def save_available_feature_extractor(output_dir: str = "configs/"):
    facebook_models = [
        "facebook/dinov2-small",
        "facebook/dinov2-base",
        "facebook/dinov2-large",
    ]
    efficientnet_models = [
        "efficientnet-b0",
        "efficientnet-b1",
        "efficientnet-b2",
    ]
    google_models = [
        "google/vit-base-patch16-224-in21k",
        "google/vit-base-patch32-224-in21k",
    ]
    dummy_models = ["dummy"]
    available_models = {}

    for model_name in facebook_models + efficientnet_models + google_models + dummy_models:
        model = get_feature_extractor(model_name)
        available_models[model_name] = {
            "type": model.__class__.__name__,
            "model_size": model.model_size,
        }

    with open(os.path.join(output_dir, "available_feature_extractors.json"), "w") as f:
        json.dump(available_models, f, indent=2)
