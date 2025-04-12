from typing import Tuple


def parse_box(box) -> list[Tuple[int, int]]:
    return [[int(box[i]), int(box[i + 1])] for i in range(0, len(box), 2)]


def parse_paddle_ocr_result(result) -> list:
    result_total = []
    for bbox, text, confidence in zip(result.boxes, result.text, result.cls_scores):
        tmp = {
            "confidence": round(confidence, 2),
            "text": text,
            "text_region": parse_box(bbox),
        }

        result_total.append(tmp)
    return result_total
