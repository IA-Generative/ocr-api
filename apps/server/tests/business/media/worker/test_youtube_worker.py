import time
from unittest.mock import patch

import pytest

from business.media.worker.youtube_worker import YOUTUBE_CONTENT_TYPE, YoutubeTranscriptionWorker
from business.media.models.youtube_transcript import YoutubeTranscriptError
from src.schemas.audio import LanguageTranscript, Segmentation
from src.schemas.input import InputForm
from src.schemas.task import TaskModel, TaskStatus


def _make_task(content_type: str = YOUTUBE_CONTENT_TYPE, source_url: str = "https://youtu.be/xxxxxxxxxxx") -> TaskModel:
    now = int(time.time())
    return TaskModel(
        id="task-1",
        user_id="user-1",
        type="default",
        status=TaskStatus.CREATED.value,
        created_at=now,
        updated_at=now,
        input=InputForm(
            raw_filename=source_url,
            content_type=content_type,
            ext="",
            size=0,
            source_url=source_url,
        ),
    )


@pytest.fixture
def worker():
    return YoutubeTranscriptionWorker(name="youtube-transcription-worker")


def test_is_applicable_true_for_youtube_content_type(worker):
    task = _make_task()
    assert worker.is_applicable(task) is True


def test_is_applicable_false_for_other_content_type(worker):
    task = _make_task(content_type="application/pdf")
    assert worker.is_applicable(task) is False


def test_is_applicable_false_without_input():
    worker = YoutubeTranscriptionWorker(name="w")
    task = _make_task()
    task.input = None
    assert worker.is_applicable(task) is False


def test_process_task_success_stores_transcription(worker):
    task = _make_task()
    fr_transcript = LanguageTranscript(
        language="fr",
        is_original=False,
        segmentations=[
            Segmentation(start_time=0.0, end_time=2.0, label="transcription", text="Bonjour"),
            Segmentation(start_time=2.0, end_time=4.0, label="transcription", text="le monde"),
        ],
        text="Bonjour le monde",
    )
    en_transcript = LanguageTranscript(
        language="en",
        is_original=False,
        segmentations=[Segmentation(start_time=0.0, end_time=2.0, label="transcription", text="Hello world")],
        text="Hello world",
    )

    with (
        patch("business.media.worker.youtube_worker.task_table") as mock_task_table,
        patch(
            "business.media.worker.youtube_worker.fetch_youtube_transcript",
            return_value=([fr_transcript, en_transcript], "fr", 4.0),
        ) as mock_fetch,
    ):
        mock_task_table.update_task.side_effect = lambda task_id, form_data: task

        result = worker.process_task(task)

        mock_fetch.assert_called_once_with(task.input.source_url, languages=worker.languages)
        assert mock_task_table.update_task.call_count == 2

        first_call, second_call = mock_task_table.update_task.call_args_list
        assert first_call.kwargs["form_data"].status == TaskStatus.IN_PROGRESS.value

        completed_form = second_call.kwargs["form_data"]
        assert completed_form.status == TaskStatus.COMPLETED.value
        assert completed_form.output.transcription_text == "Bonjour le monde"
        assert completed_form.output.segmentations == fr_transcript.segmentations
        assert completed_form.output.transcripts == [fr_transcript, en_transcript]
        assert completed_form.output.extras["duration"] == 4.0
        assert completed_form.output.extras["default_language"] == "fr"
        assert result is task


def test_process_task_failure_marks_task_failed(worker):
    task = _make_task()

    with (
        patch("business.media.worker.youtube_worker.task_table") as mock_task_table,
        patch(
            "business.media.worker.youtube_worker.fetch_youtube_transcript",
            side_effect=YoutubeTranscriptError("Aucun sous-titre disponible pour cette vidéo"),
        ),
    ):
        mock_task_table.update_task.side_effect = lambda task_id, form_data: task

        worker.process_task(task)

        assert mock_task_table.update_task.call_count == 2
        failed_form = mock_task_table.update_task.call_args_list[-1].kwargs["form_data"]
        assert failed_form.status == TaskStatus.FAILED.value
        assert "Aucun sous-titre" in failed_form.extras["error"]
