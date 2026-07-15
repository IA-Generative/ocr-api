from pathlib import Path

import pytest

from business.media.models.youtube_transcript import (
    YoutubeTranscriptError,
    _clean_caption_text,
    _collect_transcripts,
    _parse_vtt,
    _select_default_language,
    _timestamp_to_seconds,
    fetch_youtube_transcript,
)
from src.schemas.audio import LanguageTranscript, Segmentation

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "data" / "media"


def _write_vtt(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_timestamp_to_seconds_hms():
    assert _timestamp_to_seconds("00:01:02.500") == pytest.approx(62.5)


def test_timestamp_to_seconds_ms_only():
    assert _timestamp_to_seconds("01:02.500") == pytest.approx(62.5)


def test_clean_caption_text_strips_tags():
    assert _clean_caption_text("Hello <c>world</c>\nfoo") == "Hello world foo"


def test_parse_vtt_deduplicates_consecutive_identical_cues(tmp_path):
    vtt = _write_vtt(
        tmp_path,
        "sample.vtt",
        (
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:02.000\n"
            "Bonjour et bienvenue\n\n"
            "00:00:02.000 --> 00:00:04.500\n"
            "dans cette présentation.\n\n"
            "00:00:04.500 --> 00:00:04.500\n"
            "dans cette présentation.\n\n"
            "00:00:05.000 --> 00:00:07.200\n"
            "Passons à la suite.\n"
        ),
    )

    segments = _parse_vtt(vtt)

    assert [s.text for s in segments] == [
        "Bonjour et bienvenue",
        "dans cette présentation.",
        "Passons à la suite.",
    ]
    assert segments[0].start_time == pytest.approx(0.0)
    assert segments[0].end_time == pytest.approx(2.0)
    assert segments[-1].start_time == pytest.approx(5.0)
    assert segments[-1].end_time == pytest.approx(7.2)
    assert all(s.label == "transcription" for s in segments)


def test_parse_vtt_skips_empty_cues(tmp_path):
    vtt = _write_vtt(
        tmp_path,
        "empty.vtt",
        ("WEBVTT\n\n00:00:00.000 --> 00:00:01.000\n   \n\n00:00:01.000 --> 00:00:02.000\nTexte valide\n"),
    )

    segments = _parse_vtt(vtt)

    assert len(segments) == 1
    assert segments[0].text == "Texte valide"


def _write_caption_file(tmp_path: Path, video_id: str, lang: str, text: str = "Bonjour") -> None:
    (tmp_path / f"{video_id}.{lang}.vtt").write_text(
        f"WEBVTT\n\n00:00:00.000 --> 00:00:02.000\n{text}\n",
        encoding="utf-8",
    )


def test_collect_transcripts_parses_each_language(tmp_path):
    _write_caption_file(tmp_path, "abc123", "fr", "Bonjour")
    _write_caption_file(tmp_path, "abc123", "en", "Hello")

    transcripts = _collect_transcripts(tmp_path, "abc123")

    by_language = {t.language: t for t in transcripts}
    assert set(by_language) == {"fr", "en"}
    assert by_language["fr"].text == "Bonjour"
    assert by_language["fr"].is_original is False
    assert by_language["en"].text == "Hello"


def test_collect_transcripts_marks_original_language(tmp_path):
    _write_caption_file(tmp_path, "abc123", "fr", "Bonjour")
    _write_caption_file(tmp_path, "abc123", "ja-orig", "こんにちは")

    transcripts = _collect_transcripts(tmp_path, "abc123")

    by_language = {t.language: t for t in transcripts}
    assert set(by_language) == {"fr", "ja"}
    assert by_language["ja"].is_original is True
    assert by_language["fr"].is_original is False


def test_collect_transcripts_skips_empty_files(tmp_path):
    (tmp_path / "abc123.de.vtt").write_text("WEBVTT\n", encoding="utf-8")
    _write_caption_file(tmp_path, "abc123", "fr", "Bonjour")

    transcripts = _collect_transcripts(tmp_path, "abc123")

    assert {t.language for t in transcripts} == {"fr"}


def test_collect_transcripts_returns_empty_when_no_files(tmp_path):
    assert _collect_transcripts(tmp_path, "abc123") == []


def _make_transcript(language: str, is_original: bool = False) -> LanguageTranscript:
    return LanguageTranscript(
        language=language,
        is_original=is_original,
        segmentations=[Segmentation(start_time=0.0, end_time=1.0, label="transcription", text="x")],
        text="x",
    )


def test_select_default_language_prefers_original():
    transcripts = [_make_transcript("fr"), _make_transcript("ja", is_original=True), _make_transcript("en")]

    assert _select_default_language(transcripts, ["fr", "en"]) == "ja"


def test_select_default_language_prefers_requested_order_without_original():
    transcripts = [_make_transcript("en"), _make_transcript("fr")]

    assert _select_default_language(transcripts, ["fr", "en"]) == "fr"


def test_select_default_language_falls_back_to_any_available():
    transcripts = [_make_transcript("de")]

    assert _select_default_language(transcripts, ["fr", "en"]) == "de"


def test_fetch_youtube_transcript_raises_when_no_subtitle(monkeypatch):
    class _FakeYDL:
        def __init__(self, opts):
            self.opts = opts

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def extract_info(self, url, download=True):
            return {"id": "novtt", "duration": 42.0}

    monkeypatch.setattr("business.media.models.youtube_transcript.yt_dlp.YoutubeDL", _FakeYDL)

    with pytest.raises(YoutubeTranscriptError, match="Aucun sous-titre"):
        fetch_youtube_transcript("https://www.youtube.com/watch?v=xxxxxxxxxxx")
