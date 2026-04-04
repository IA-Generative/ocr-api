import json
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import paddle
from loguru import logger
from PIL import Image
from tqdm import tqdm
from hashlib import sha256

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
)

_DATASET_URL = "https://guillaumejaume.github.io/FUNSD/dataset.zip"
_DATASET_ZIP = Path("data/FUNSD.zip")
_EXTRACT_DIR = Path("data/FUNSD")
_IMAGE_SIZE = (320, 32)

Sample = tuple[str, dict]


def _download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"📥 Téléchargement {dst.name} …")
    urllib.request.urlretrieve(url, dst)
    logger.info(f"✔️  Téléchargé → {dst}")


def _extract(zip_path: Path, dst: Path) -> None:
    logger.info(f"📂 Extraction {zip_path.name} …")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dst)
    logger.info(f"✔️  Extrait → {dst}")


def _load_split(images_dir: Path, annotations_dir: Path, desc: str) -> list[Sample]:
    samples: list[Sample] = []
    for img_path in tqdm(sorted(images_dir.glob("*.png")), desc=desc):
        ann_path = annotations_dir / img_path.with_suffix(".json").name
        if not ann_path.exists():
            logger.warning(f"⚠️  Annotation manquante : {img_path.name}, skip")
            continue
        label = json.loads(ann_path.read_text(encoding="utf-8"))
        samples.append((str(img_path), label))
    return samples


class FunsdDataset(paddle.io.Dataset):
    def __init__(self, url: str = _DATASET_URL) -> None:
        if not _DATASET_ZIP.exists():
            _download(url, _DATASET_ZIP)
        if not _EXTRACT_DIR.exists():
            _extract(_DATASET_ZIP, _EXTRACT_DIR)

        base = _EXTRACT_DIR / "dataset"
        self.samples: list[Sample] = [
            *_load_split(
                base / "training_data" / "images",
                base / "training_data" / "annotations",
                desc="train",
            ),
            *_load_split(
                base / "testing_data" / "images",
                base / "testing_data" / "annotations",
                desc="test",
            ),
        ]
        logger.info(f"✅ {len(self.samples)} échantillons chargés")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[np.ndarray, dict]:
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        arr = np.array(img, dtype="float32")
        return arr, label  # (C, H, W)


class FunsdRecognitionDataset(paddle.io.Dataset):
    def __init__(self, url: str = _DATASET_URL) -> None:
        funsd_dataset = FunsdDataset(url)
        self.samples: list[tuple[str, str]] = []
        self.folder = Path("data/funsd_recognition")
        self.folder_images = self.folder / "images"
        self.folder_images.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ {len(self.samples)} échantillons chargés pour reconnaissance")
        progress_bar = tqdm(
            funsd_dataset,
            total=len(funsd_dataset),
            desc="Préparation données reconnaissance",
        )
        for sample in progress_bar:
            self.samples.extend(self.save_for_recognition(sample))
            progress_bar.set_postfix({"samples": len(self.samples)})
        dict_char = set()
        for _, text in self.samples:
            dict_char.update(set(text))
        with open(self.folder / "dict.txt", "w", encoding="utf-8") as f:
            for c in sorted(dict_char):
                f.write(f"{c}\n")
        with open(self.folder / "train.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(f"{os.path.basename(p)}\t{t}" for p, t in self.samples[: int(0.8 * len(self.samples))]))
        with open(self.folder / "val.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(f"{os.path.basename(p)}\t{t}" for p, t in self.samples[int(0.8 * len(self.samples)) :]))

    def save_for_recognition(self, sample: tuple[np.ndarray, dict]) -> list[tuple[str, str]]:
        image, annotations = sample
        results: list[tuple[str, str]] = []
        dict_char: set[str] = set()
        for item in annotations.get("form", []):
            box = item["box"]
            text = item["text"]  # list of words
            dict_char.update(set(text))
            image_crop = image[box[1] : box[3], box[0] : box[2]]  #
            hash_crop = sha256(image_crop.tobytes()).hexdigest()
            path_crop = self.folder_images / f"{hash_crop}.png"
            img_crop = Image.fromarray((image_crop * 255).astype("uint8"))
            if not path_crop.exists():
                img_crop.save(path_crop)
            results.append((str(path_crop), text))

        return results

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[np.ndarray, str]:
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        img = img.resize(_IMAGE_SIZE)
        arr = np.array(img, dtype="float32") / 255.0
        arr = arr.transpose((2, 0, 1))  # (C, H, W)
        return arr, label


if __name__ == "__main__":
    logger.info("=" * 40 + " Test FunsdDataset " + "=" * 40)
    ds = FunsdDataset()
    logger.info(f"Taille : {len(ds)}")
    img, ann = ds[0]
    logger.info(f"Image size : {img.size} | Clés annotation : {list(ann.keys())}")
    logger.info("=" * 40 + " Fin " + "=" * 40)
    FunsdRecognitionDataset()
