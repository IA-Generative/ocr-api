from datasets import load_dataset
from typing import Iterator, Any
from PIL import Image
from datasets.iterable_dataset import IterableDataset
from pdf2image import convert_from_bytes
from langfuse import Langfuse
import hashlib
import base64
from io import BytesIO
from datasets.iterable_dataset import IterableColumn


def pil_image_to_base64(img: Image.Image) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def base64_to_pil_image(b64_string: str) -> Image.Image:
    image_data = base64.b64decode(b64_string)
    return Image.open(BytesIO(image_data))


class StreamingDatasetWrapper:
    """
    Wrapper générique pour itérer sur un dataset Hugging Face en mode streaming,
    avec une interface de type liste (itérable, mais pas d'accès direct par index).
    """

    def __init__(
        self,
        dataset_name: str,
        split: str = "train",
        cache_dir: str = "./datasets/hf_cache",
        **kwargs,
    ):
        self.dataset_name = dataset_name
        self.dataset: IterableDataset = load_dataset(
            dataset_name, split=split, streaming=True, cache_dir=cache_dir, **kwargs
        )

    def __iter__(self) -> Iterator[Any]:
        return iter(self.dataset)

    def __len__(self):
        raise NotImplementedError("La longueur n'est pas disponible en mode streaming.")

    def __getitem__(self, idx):
        raise NotImplementedError("L'accès par index n'est pas supporté en mode streaming.")


class PixParseDataset(StreamingDatasetWrapper):
    """
    Wrapper pour le dataset PixParse.
    """

    def __init__(
        self,
        split: str = "train",
        cache_dir: str = "./dataset/hf_cache",
        langfuse: Langfuse = None,
        **kwargs,
    ):
        super().__init__("pixparse/pdfa-eng-wds", split=split, cache_dir=cache_dir, **kwargs)
        self.langfuse = langfuse
        self.dataset_name = "pixparse_pdfa_eng_wds"
        if self.langfuse:
            self.langfuse.create_dataset(name=self.dataset_name)

    def __getitem__(self, idx: int) -> IterableColumn:
        return self.dataset[idx]

    def __iter__(self) -> Iterator[tuple[list[str], list[Image.Image]]]:
        for index, item in enumerate(self.dataset):
            sources = []
            pages_texts = []
            pdf_page_images = []
            for i, page in enumerate(item["json"]["pages"]):
                page_text = "\n".join(page["lines"]["text"])
                pages_texts.append(page_text)
                image = convert_from_bytes(item["pdf"], dpi=300, first_page=i + 1, last_page=i + 1)[0]
                pdf_page_images.append(image)
                sources.append(item["__url__"])
                if self.langfuse:
                    self.langfuse.create_dataset_item(
                        dataset_name=self.dataset_name,
                        input={
                            "page_number": i + 1,
                            "source": item["__url__"],
                            "index": index,
                            "image_size": image.size,
                        },
                        expected_output={"text": page_text},
                        id=hashlib.sha256(pil_image_to_base64(image).encode()).hexdigest(),
                    )

            yield (sources, pages_texts, pdf_page_images)
