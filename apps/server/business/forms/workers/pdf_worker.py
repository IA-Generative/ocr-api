import fitz
from PIL import Image
import io

from src.schemas.box import Bbox
from src.schemas.template import FormEntry
from services.base.worker import BaseWorker
from src.schemas.output import Page
from io import BytesIO
import time


from src.logger import logger
from src.schemas.task import TaskModel, TaskStatus, TaskUpdateForm, task_table


class PDFFormsExtractorWorker(BaseWorker):
    def __init__(
        self,
        name,
        file_connector,
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    ):
        super().__init__(
            name,
            file_connector,
            models=models,
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input.content_type == "application/pdf":
            return False
        t = time.time()
        tmp_filename = self.get_content_file(task=task)
        doc: fitz.Document = fitz.open(tmp_filename)

        logger.debug(
            f"Time to open PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
        )

        return doc.is_form_pdf

    def predict_on_pages(self, task: TaskModel, pages: list[Image.Image]) -> TaskModel:
        extra_log = {
            "task_id": task.id,
            "user_id": task.user_id,
            "worker_name": self.name,
        }
        if task.input.content_type != "application/pdf":
            logger.error(
                f"Invalid content type {task.input.content_type} for task {task.id}. Expected application/pdf.",
                extra=extra_log,
            )
            return task
        t = time.time()
        tmp_filename = self.get_content_file(task=task)
        doc: fitz.Document = fitz.open(tmp_filename)
        logger.debug(
            f"Time to open PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
            extra=extra_log,
        )
        if not doc.is_form_pdf:
            return task

        task = self.set_output(task=task, total_pages=len(pages))
        filename = task.input.raw_filename
        client_s3 = self.file_connector.client
        task.output.pages = [Page(page=i) for i in range(len(pages))]
        logger.debug(
            f"[worker {self.name}][Size input images {len(pages)}][Size empty pages {len(task.output.pages)}]",
            extra=extra_log,
        )

        form_bboxs, forms_entries = self.process(task=task)

        for bbox, form_entry, page in zip(
            form_bboxs,
            forms_entries,
            task.output.pages,
        ):
            page.boxes = bbox
            page.form_entries = form_entry
            page.page_url = None

        task.output.text = ""
        for i in range(0, len(pages), self.batch_size):
            t_predict = time.time()
            batch = pages[i : i + self.batch_size]
            logger.debug(
                f"{filename} for task {task.id}, batch [{i}:{i + self.batch_size}][total: {len(pages)}]",
                extra=extra_log,
            )
            partial_result = task.output.pages[i : i + self.batch_size]

            for j, image in enumerate(batch):
                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                key = f"{task.user_id}/{task.id}/images/page_{i + j}.jpg"
                client_s3.upload_fileobj(buffer, self.file_connector.bucket_name, key)
                logger.debug(
                    f"[worker {self.name}]Uploaded page {i + j} to {key}",
                    extra=extra_log,
                )
                signed_url = client_s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.file_connector.bucket_name, "Key": key},
                    ExpiresIn=3600,  # 1h
                )
                partial_result[j].page_url = signed_url

            task.output.pages[i : i + self.batch_size] = partial_result

            page_range = f"{i + 1}" if len(batch) == 1 else f"{i + 1}-{i + self.batch_size}"
            logger.debug(
                f"{filename} time to process page {page_range} - {time.time() - t_predict:.2f}s",
                extra=extra_log,
            )

            percentage = (i + len(batch)) / task.output.total_pages
            logger.debug(
                f"[worker {self.name}][Current percentage {100 * percentage:.2f}%]",
                extra=extra_log,
            )
            task.output.set_text()
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.IN_PROGRESS.value,
                    percentage=percentage * self.worker_weight,
                    output=task.output,
                    extras=task.extras,
                ),
            )
            logger.debug(
                task.extras,
                extra=extra_log,
            )
        return task

    def process(self, task: TaskModel) -> tuple[list[list[Bbox]], list[list[FormEntry]]]:
        t = time.time()
        tmp_filename = self.get_content_file(task=task)
        doc: fitz.Document = fitz.open(tmp_filename)
        logger.debug(
            f"[worker {self.name}]Time to open PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
            extra={"task_id": task.id, "user_id": task.user_id},
        )

        dpi = 150
        scale = dpi / 72
        forms_bboxes: list[list[Bbox]] = []
        forms_entries: list[list[FormEntry]] = []
        t = time.time()
        for page in doc:
            page_forms: list[FormEntry] = []
            page_bboxes: list[Bbox] = []
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

            for widget in page.widgets():
                rect = widget.rect
                name = widget.field_name
                value = widget.field_value

                x0, y0 = rect.x0 * scale / img.width, rect.y0 * scale / img.height
                x1, y1 = rect.x1 * scale / img.width, rect.y1 * scale / img.height

                page_forms.append(FormEntry(key=name, value=value))

                page_bboxes.append(
                    Bbox(
                        x=x0,
                        y=y0,
                        width=x1 - x0,
                        height=y1 - y0,
                        confidence=1.0,
                        text=f"{name} = {value}",
                    )
                )
            forms_bboxes.append(page_bboxes)
            forms_entries.append(page_forms)
        logger.debug(
            f"[worker {self.name}]Time to process PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
            extra={"task_id": task.id, "user_id": task.user_id},
        )
        return forms_bboxes, forms_entries
