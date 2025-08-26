from src.schemas.output import Page
from src.schemas.box import Bbox
from src.utils.bboxes import sort_bboxes_reading_order, get_text_from_list_bboxes

import jiwer


def set_text(page: Page, delta_y: float = 0.005) -> str:
    pages_content_per_page = []

    page_lines_content = []
    checkboxes = [
        Bbox(
            x=checkbox.x,
            y=checkbox.y,
            confidence=checkbox.confidence,
            height=checkbox.height,
            width=checkbox.width,
            text="[x]" if checkbox.is_checked else "[ ]",
        )
        for checkbox in page.checkboxes
    ]

    sorted_bboxes = sort_bboxes_reading_order(bboxes=page.boxes + checkboxes, delta_y=delta_y)
    for line_sorted_boxes in sorted_bboxes:
        text_line = get_text_from_list_bboxes(line_sorted_boxes)
        page_lines_content.append(text_line)

    page_content = "\n".join(page_lines_content)
    pages_content_per_page.append(page_content)

    return "\n".join(pages_content_per_page)


def cer(reference: str, hypothesis: str) -> float:
    """Compute Character Error Rate (CER) between reference and hypothesis strings."""
    return jiwer.cer(reference, hypothesis)


def wer(reference: str, hypothesis: str) -> float:
    """Compute Word Error Rate (WER) between reference and hypothesis strings."""
    return jiwer.wer(reference, hypothesis)


def iou_text(reference: str, hypothesis: str) -> float:
    """Compute Intersection over Union (IoU) between reference and hypothesis strings."""
    ref_set = set(reference.split())
    hyp_set = set(hypothesis.split())
    intersection = ref_set.intersection(hyp_set)
    union = ref_set.union(hyp_set)
    if not union:
        return 1.0 if not intersection else 0.0
    return len(intersection) / len(union)


def presence_words(reference: str, hypothesis: str) -> float:
    """Compute the presence of words from the reference in the hypothesis."""
    ref_set = reference.split()
    hyp_set = hypothesis.split()
    n_words_hyp = len(hyp_set)
    n_words_ref = len(ref_set)
    for word in hyp_set:
        if word in ref_set:
            ref_set.remove(word)

    return (n_words_ref - len(ref_set)) / (n_words_hyp + n_words_ref) if (n_words_hyp + n_words_ref) > 0 else 0.0


def precision(reference: str, hypothesis: str) -> float:
    """Compute the precision: proportion de mots de l'hypothèse présents dans la référence."""
    ref_set = set(reference.split())
    hyp_set = set(hypothesis.split())
    if not hyp_set:
        return 1.0 if not ref_set else 0.0
    intersection = ref_set & hyp_set
    return len(intersection) / len(hyp_set)


def recall(reference: str, hypothesis: str) -> float:
    """Compute the recall: proportion de mots de la référence retrouvés dans l'hypothèse."""
    ref_set = set(reference.split())
    hyp_set = set(hypothesis.split())
    if not ref_set:
        return 1.0
    intersection = ref_set & hyp_set
    return len(intersection) / len(ref_set)


def f1_score(reference: str, hypothesis: str) -> float:
    """Compute the F1-score (harmonic mean of precision and recall) sur les mots."""
    p = precision(reference, hypothesis)
    r = recall(reference, hypothesis)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)
