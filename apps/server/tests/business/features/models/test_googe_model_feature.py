from PIL import Image
from business.features.models.google import GoogleImageFeatureExtractor


def test_get_feature_from_google_image():
    extractor = GoogleImageFeatureExtractor()
    image = Image.new("RGB", (224, 224))
    features = extractor.get_vector_from_image(image)
    assert len(features) == extractor.model_size
