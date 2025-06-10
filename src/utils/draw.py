from PIL import Image, ImageDraw, ImageFont
from src.schemas.box import Bbox


def draw_normalized_bboxes(
    image: Image.Image, boxes: list[Bbox], outline="red", width=2, font: ImageFont.ImageFont = None
):
    """
    Dessine les boîtes normalisées (x, y, w, h) sur l'image PIL.
    :param image: PIL.Image original
    :param boxes: liste d'objets avec .x, .y, .width, .height (normalisés)
    :param outline: couleur de contour
    :param width: épaisseur du trait en pixels
    """
    if font is None:
        try:
            # Police intégrée si dispo
            font = ImageFont.load_default()
        except Exception as e:
            font = None
            print(e)
    draw = ImageDraw.Draw(image)
    img_w, img_h = image.size
    for bb in boxes:
        # Convertit de coord normalisées vers pixels
        x0 = bb.x * img_w
        y0 = bb.y * img_h
        x1 = (bb.x + bb.width) * img_w
        y1 = (bb.y + bb.height) * img_h
        draw.rectangle([x0, y0, x1, y1], outline=outline, width=width)
        label = f"[{100*bb.confidence:.1f}]{bb.text}"
        if font:
            bbox = draw.textbbox((0, 0), label, font=font)
            text_h = bbox[3] - bbox[1]
        else:
            # Estimation par défaut
            text_h = 10

        text_x = x0
        text_y = max(0, y0 - text_h - 2)
        draw.text((text_x, text_y), label, fill=outline, font=font)
    return image
