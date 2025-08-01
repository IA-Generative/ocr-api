from PIL import Image
from business.features.models.efficientnet_features import (
    EfficientImageFeatureExtractor,
)


def test_get_vector_from_image():
    extractor = EfficientImageFeatureExtractor()
    image = Image.new("RGB", (224, 224))
    features = extractor.get_vector_from_image(image)
    assert features is not None
    assert len(features) == 1280
