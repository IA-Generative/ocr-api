from __future__ import annotations

import argparse
import time

import numpy as np
from jiwer import wer as _jiwer_wer
from paddleocr import PaddleOCR
from rapidfuzz.distance import Levenshtein as _Levenshtein
from tqdm import tqdm

from datasets.funsd import FunsdDataset

try:
    from shapely.geometry import box as _shapely_box
except ImportError:  # pragma: no cover
    _shapely_box = None  # type: ignore[assignment]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--rec_model_dir",
        default=None,
        help="Path to an exported inference rec model dir (contains inference.pdmodel). "
        "Uses the default PP-OCRv3 model if omitted.",
    )
    parser.add_argument(
        "--det_model_dir",
        default=None,
        help="Path to an exported inference det model dir. Uses default if omitted.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def _to_xyxy(box: list) -> list[float] | None:
    """Normalise any box format to [x1, y1, x2, y2] floats.

    Accepts:
      - [x1, y1, x2, y2]           (4 scalars)
      - [[x,y], [x,y], [x,y], [x,y]]  (polygon)

    Returns None if the box is degenerate (zero area).
    """
    if len(box) == 4 and not isinstance(box[0], (list, tuple)):
        x1, y1, x2, y2 = (float(v) for v in box)
    else:
        pts = [(float(p[0]), float(p[1])) for p in box]
        x1 = min(p[0] for p in pts)
        y1 = min(p[1] for p in pts)
        x2 = max(p[0] for p in pts)
        y2 = max(p[1] for p in pts)

    # Guarantee x1 ≤ x2, y1 ≤ y2 and non-negative coords
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    x1, y1 = max(0.0, x1), max(0.0, y1)

    if (x2 - x1) <= 0 or (y2 - y1) <= 0:
        return None  # degenerate box, skip

    return [x1, y1, x2, y2]


def iou(boxA: list[float], boxB: list[float]) -> float:
    """Compute IoU between two normalised [x1, y1, x2, y2] boxes."""
    if _shapely_box is not None:
        a = _shapely_box(*boxA)
        b = _shapely_box(*boxB)
        inter = a.intersection(b).area
        union = a.union(b).area
        return float(inter / union) if union > 0 else 0.0
    # numeric fallback (no Shapely)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter = max(0.0, xB - xA) * max(0.0, yB - yA)
    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    denom = areaA + areaB - inter
    return float(inter / denom) if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# Text metrics  (CER / WER)
# ---------------------------------------------------------------------------


def cer(pred: str, ref: str) -> float:
    """Character Error Rate via rapidfuzz."""
    if not ref:
        return 0.0 if not pred else 1.0
    return _Levenshtein.distance(pred, ref) / len(ref)


def wer(pred: str, ref: str) -> float:
    """Word Error Rate via jiwer (reference first, then hypothesis)."""
    return float(_jiwer_wer(ref, pred))


def _match_texts(
    pred_boxes: list[list[float]],
    pred_texts: list[str],
    gt_boxes: list[list[float]],
    gt_texts: list[str],
    iou_threshold: float = 0.5,
) -> tuple[list[str], list[str]]:
    """For each GT box, find the best-matching prediction (by IoU) and return aligned pairs."""
    matched_preds: list[str] = []
    matched_refs: list[str] = []
    for gb, gt in zip(gt_boxes, gt_texts):
        best_score, best_text = 0.0, ""
        for pb, pt in zip(pred_boxes, pred_texts):
            s = iou(pb, gb)
            if s > best_score:
                best_score, best_text = s, pt
        if best_score >= iou_threshold:
            matched_preds.append(best_text)
            matched_refs.append(gt)
    return matched_preds, matched_refs


def compute_cer_wer(
    all_pred_boxes: list[list[list[float]]],
    all_pred_texts: list[list[str]],
    all_gt_boxes: list[list[list[float]]],
    all_gt_texts: list[list[str]],
    iou_threshold: float = 0.5,
) -> tuple[float, float]:
    """Return mean CER and WER over the dataset."""
    cer_scores, wer_scores = [], []
    for pb, pt, gb, gt in zip(all_pred_boxes, all_pred_texts, all_gt_boxes, all_gt_texts):
        preds, refs = _match_texts(pb, pt, gb, gt, iou_threshold)
        for p, r in zip(preds, refs):
            cer_scores.append(cer(p, r))
            wer_scores.append(wer(p, r))
    if not cer_scores:
        return 1.0, 1.0
    return float(np.mean(cer_scores)), float(np.mean(wer_scores))


def average_precision(
    pred_boxes: list[list[float]],
    pred_scores: list[float],
    gt_boxes: list[list[float]],
    iou_threshold: float = 0.5,
) -> float:
    """Compute Average Precision for a single image at a given IoU threshold."""
    if not gt_boxes:
        return 1.0 if not pred_boxes else 0.0
    if not pred_boxes:
        return 0.0

    # Sort predictions by descending confidence
    order = np.argsort(pred_scores)[::-1]
    pred_boxes = [pred_boxes[i] for i in order]
    pred_scores = [pred_scores[i] for i in order]

    matched = [False] * len(gt_boxes)
    tp = []
    fp = []

    for pb in pred_boxes:
        best_iou, best_j = 0.0, -1
        for j, gb in enumerate(gt_boxes):
            s = iou(pb, gb)
            if s > best_iou:
                best_iou, best_j = s, j

        if best_iou >= iou_threshold and not matched[best_j]:
            tp.append(1)
            fp.append(0)
            matched[best_j] = True
        else:
            tp.append(0)
            fp.append(1)

    tp_cum = np.cumsum(tp)
    fp_cum = np.cumsum(fp)
    recalls = tp_cum / len(gt_boxes)
    precisions = tp_cum / (tp_cum + fp_cum)

    # Area under the precision-recall curve (11-point interpolation)
    ap = 0.0
    for t in np.linspace(0, 1, 11):
        p = precisions[recalls >= t].max() if np.any(recalls >= t) else 0.0
        ap += p / 11
    return float(ap)


def compute_map(
    all_pred_boxes: list[list[list[float]]],
    all_pred_scores: list[list[float]],
    all_gt_boxes: list[list[list[float]]],
    iou_threshold: float = 0.5,
) -> float:
    """Compute mean Average Precision over a dataset."""
    aps = [
        average_precision(pb, ps, gb, iou_threshold)
        for pb, ps, gb in zip(all_pred_boxes, all_pred_scores, all_gt_boxes)
    ]
    return float(np.mean(aps))


# ---------------------------------------------------------------------------
# Evaluation loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = _parse_args()

    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        ocr_version="PP-OCRv3",
        rec_model_dir=args.rec_model_dir,
        det_model_dir=args.det_model_dir,
    )

    if args.rec_model_dir:
        print(f"[INFO] Using trained rec model: {args.rec_model_dir}")
    else:
        print("[INFO] Using default PP-OCRv3 rec model")
    dataset = FunsdDataset()
    all_pred_boxes: list[list[list[float]]] = []
    all_pred_scores: list[list[float]] = []
    all_pred_texts: list[list[str]] = []
    all_gt_boxes: list[list[list[float]]] = []
    all_gt_texts: list[list[str]] = []
    inference_times: list[float] = []
    progress_bar = tqdm(dataset, desc="Évaluation")

    for image, annotations in progress_bar:
        t0 = time.perf_counter()
        results = ocr.predict(image)
        inference_times.append(time.perf_counter() - t0)

        # Predicted boxes + scores + texts
        pred_boxes, pred_scores, pred_texts = [], [], []
        for entry in results:
            for poly, score, text in zip(
                entry.get("rec_boxes", []),
                entry.get("rec_scores", []),
                entry.get("rec_texts", []),
            ):
                box = _to_xyxy(poly)
                if box is not None:
                    pred_boxes.append(box)
                    pred_scores.append(float(score))
                    pred_texts.append(str(text))

        # GT boxes + texts from FUNSD
        gt_boxes, gt_texts = [], []
        for item in annotations.get("form", []):
            box = _to_xyxy(item["box"])
            if box is not None:
                gt_boxes.append(box)
                # FUNSD words list → join into a single string per box
                words = item.get("words", [])
                gt_texts.append(" ".join(w["text"] for w in words) if words else item.get("text", ""))

        all_pred_boxes.append(pred_boxes)
        all_pred_scores.append(pred_scores)
        all_pred_texts.append(pred_texts)
        all_gt_boxes.append(gt_boxes)
        all_gt_texts.append(gt_texts)

        progress_bar.set_postfix(
            {
                "preds": len(pred_boxes),
                "gt": len(gt_boxes),
                "ms": f"{inference_times[-1] * 1000:.0f}",
            }
        )

    map50 = compute_map(all_pred_boxes, all_pred_scores, all_gt_boxes, iou_threshold=0.5)
    map75 = compute_map(all_pred_boxes, all_pred_scores, all_gt_boxes, iou_threshold=0.75)
    mean_cer, mean_wer = compute_cer_wer(all_pred_boxes, all_pred_texts, all_gt_boxes, all_gt_texts, iou_threshold=0.5)

    t_arr = np.array(inference_times) * 1000  # ms

    def _grade(value: float, thresholds: tuple[float, float], low_is_good: bool) -> str:
        """Return ✅ / ⚠️ / ❌ based on thresholds (good, acceptable)."""
        lo, hi = thresholds
        if low_is_good:
            return "✅" if value <= lo else ("⚠️ " if value <= hi else "❌")
        else:
            return "✅" if value >= lo else ("⚠️ " if value >= hi else "❌")

    print(f"\n{'─' * 55}")
    print(f"📊  Résultats sur {len(dataset)} images FUNSD")
    print(f"{'─' * 55}")

    print("\n  Détection de zones (boîtes englobantes)")
    print(f"  {'Métrique':<12} {'Valeur':>8}   {'':3}  Description")
    print(f"  {'-' * 50}")
    print(
        f"  {'mAP@0.50':<12} {map50:>8.4f}   {_grade(map50, (0.7, 0.5), False)}"
        f"  Précision moyenne à IoU≥0.50 — bon si ≥ 0.70"
    )
    print(
        f"  {'mAP@0.75':<12} {map75:>8.4f}   {_grade(map75, (0.5, 0.3), False)}"
        f"  Précision moyenne à IoU≥0.75 (critère strict) — bon si ≥ 0.50"
    )

    print("\n  Transcription du texte")
    print(f"  {'Métrique':<12} {'Valeur':>8}   {'':3}  Description")
    print(f"  {'-' * 50}")
    print(
        f"  {'CER':<12} {mean_cer:>8.4f}   {_grade(mean_cer, (0.05, 0.15), True)}"
        f"  Character Error Rate — bon si ≤ 0.05 (~5 %)"
    )
    print(
        f"  {'WER':<12} {mean_wer:>8.4f}   {_grade(mean_wer, (0.10, 0.30), True)}"
        f"  Word Error Rate — bon si ≤ 0.10 (~10 %)"
    )

    print("\n  ⏱  Temps d'inférence par image (ms)")
    print(f"  {'-' * 50}")
    print(f"  {'mean':<12} {t_arr.mean():>8.1f}   {_grade(t_arr.mean(), (500, 2000), True)}  Moyenne — bon si ≤ 500 ms")
    print(
        f"  {'median':<12} {np.median(t_arr):>8.1f}   {_grade(np.median(t_arr), (500, 2000), True)}"
        f"  Médiane (robuste aux pics)"
    )
    print(
        f"  {'p95':<12} {np.percentile(t_arr, 95):>8.1f}   {_grade(np.percentile(t_arr, 95), (1000, 3000), True)}"
        f"  95e percentile — bon si ≤ 1 000 ms"
    )
    print(f"  {'min / max':<12} {t_arr.min():>6.1f} / {t_arr.max():.1f} ms")
    print(f"{'─' * 55}\n")
