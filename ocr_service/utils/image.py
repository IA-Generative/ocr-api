from PIL import Image
import base64
import io


def image_to_base64(image: Image.Image, format="PNG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
