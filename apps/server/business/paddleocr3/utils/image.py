from PIL import Image


def crop_img(img: Image.Image, coordinates: list[float], is_normalized: bool = True):
    if is_normalized:
        width_img, height_img = img.size
        coordinates[0] = coordinates[0] * width_img
        coordinates[2] = coordinates[2] * width_img
        coordinates[1] = coordinates[1] * height_img
        coordinates[3] = coordinates[3] * height_img

    left, upper, right, lower = map(int, coordinates)

    return img.crop((left, upper, right, lower))
