from PIL import Image
from business.features.models.facebook import FacebookImageFeatureExtractor


def test_get_feature_from_facebook_image():
    extractor = FacebookImageFeatureExtractor()
    image = Image.new("RGB", (224, 224))
    features = extractor.get_vector_from_image(image)
    assert len(features) == extractor.model_size
