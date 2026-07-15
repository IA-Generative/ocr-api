import time
from typing import Optional

from src import __version__
from src.logger import logger
from src.schemas.audio import AudioTranscriptionResult
from src.schemas.task import TaskModel, TaskStatus, TaskUpdateForm, task_table

from business.media.models.youtube_transcript import fetch_youtube_transcript

YOUTUBE_CONTENT_TYPE = "video/youtube"


class YoutubeTranscriptionWorker:
    """Récupère la transcription (sous-titres) d'une vidéo YouTube via yt-dlp,
    synchronisée avec la timeline réelle de la vidéo (start_time/end_time par segment).

    Ne suit pas l'interface de ``BaseWorker`` (pas de fichier à télécharger depuis S3,
    pas de pages images) : seuls ``name``, ``is_applicable`` et ``process_task`` sont
    requis par ``Pipeline.process``.
    """

    def __init__(self, name: str, languages: Optional[list[str]] = None):
        self.name = name
        self.languages = languages or ["fr", "en"]

    def is_applicable(self, task: TaskModel) -> bool:
        return bool(task.input and task.input.content_type == YOUTUBE_CONTENT_TYPE)

    def process_task(self, task: TaskModel) -> TaskModel:
        extra_log = {"task_id": task.id, "user_id": task.user_id}
        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(status=TaskStatus.IN_PROGRESS.value, percentage=0.0),
        )

        url = task.input.source_url
        logger.info(f"[{self.name}] Fetching YouTube transcript for {url}", extra=extra_log)

        try:
            transcripts, default_language, duration = fetch_youtube_transcript(url, languages=self.languages)
        except Exception as e:
            logger.error(f"[{self.name}] Failed to fetch transcript for task {task.id}: {e}", extra=extra_log)
            return task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(status=TaskStatus.FAILED.value, extras={"error": str(e)}),
            )

        default_transcript = next(t for t in transcripts if t.language == default_language)

        output = AudioTranscriptionResult(
            type=self.name,
            model_name="yt-dlp",
            created_at=int(time.time()),
            updated_at=int(time.time()),
            version=__version__,
            segmentations=default_transcript.segmentations,
            transcription_text=default_transcript.text,
            transcripts=transcripts,
            extras={"duration": duration, "source_url": url, "default_language": default_language},
        )

        return task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(status=TaskStatus.COMPLETED.value, percentage=1.0, output=output),
        )
