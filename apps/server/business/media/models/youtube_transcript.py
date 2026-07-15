import re
import tempfile
import time
from pathlib import Path
from typing import Optional

import webvtt
import yt_dlp

from src.schemas.audio import LanguageTranscript, Segmentation

DEFAULT_LANGUAGES = ["fr", "en"]
# yt-dlp marque la piste de sous-titres automatiques dans la langue originale de la
# vidéo avec un suffixe "-orig" (ex: "ja-orig"), quel que soit le code de langue réel.
# Ce pattern est traité comme une regex par yt-dlp (subtitleslangs), d'où le ".*".
ORIGINAL_LANGUAGE_PATTERN = ".*-orig"
# Le client "web" est le plus souvent throttlé (429) sur l'endpoint des sous-titres ;
# "android"/"ios" passent généralement par une API moins limitée.
DEFAULT_PLAYER_CLIENTS = ["android", "web"]
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5

_TAG_RE = re.compile(r"<[^>]+>")
_RATE_LIMIT_MARKERS = ("429", "Too Many Requests")


class YoutubeTranscriptError(Exception):
    """Levée quand la transcription d'une vidéo YouTube ne peut pas être récupérée."""


def _extract_info_with_retry(ydl_opts: dict, url: str) -> dict:
    """Appelle yt-dlp avec un retry + backoff exponentiel sur les 429 (rate limit
    YouTube), transitoires par nature. Les autres erreurs sont levées immédiatement."""
    last_error: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as e:
            if not any(marker in str(e) for marker in _RATE_LIMIT_MARKERS):
                raise YoutubeTranscriptError(f"Impossible de récupérer la vidéo YouTube : {e}") from e
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise YoutubeTranscriptError(
        f"Limite de débit YouTube atteinte après {MAX_RETRIES} tentatives : {last_error}"
    ) from last_error


def fetch_youtube_transcript(
    url: str,
    languages: Optional[list[str]] = None,
) -> tuple[list[LanguageTranscript], str, float]:
    """Récupère les sous-titres (manuels en priorité, sinon automatiques) d'une
    vidéo YouTube via yt-dlp : la langue originale de la vidéo, plus ``languages``
    (fr/en par défaut). Chacune est optionnelle — si l'une n'existe pas, ce n'est
    pas bloquant tant qu'au moins une des trois est disponible. Sans télécharger
    la vidéo ; les segments sont horodatés et synchronisés avec le temps réel.

    Retourne (transcripts disponibles, code de la langue à utiliser par défaut,
    durée_en_secondes).
    """
    languages = languages or DEFAULT_LANGUAGES

    with tempfile.TemporaryDirectory() as tmp_dir:
        outtmpl = str(Path(tmp_dir) / "%(id)s")
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [*languages, ORIGINAL_LANGUAGE_PATTERN],
            "subtitlesformat": "vtt",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "sleep_interval_subtitles": 1,
            "extractor_args": {"youtube": {"player_client": DEFAULT_PLAYER_CLIENTS}},
            # Sans ça, l'échec du téléchargement d'UNE SEULE langue (ex: "en" rate-limité)
            # fait lever une DownloadError qui annule tout l'appel — y compris les langues
            # (fr, langue originale) déjà récupérées avec succès. `True` (et rien d'autre)
            # transforme ces échecs par langue en simples avertissements non bloquants.
            "ignoreerrors": True,
        }

        info = _extract_info_with_retry(ydl_opts, url)
        if info is None:
            raise YoutubeTranscriptError("Impossible de récupérer les informations de la vidéo YouTube")

        duration = float(info.get("duration") or 0.0)
        video_id = info.get("id", "")

        transcripts = _collect_transcripts(Path(tmp_dir), video_id)
        if not transcripts:
            raise YoutubeTranscriptError("Aucun sous-titre disponible pour cette vidéo")

        default_language = _select_default_language(transcripts, languages)
        return transcripts, default_language, duration


def _collect_transcripts(tmp_dir: Path, video_id: str) -> list[LanguageTranscript]:
    """Parse chaque fichier de sous-titres téléchargé en un ``LanguageTranscript``.
    Le suffixe "-orig" (langue parlée d'origine de la vidéo, cf ``ORIGINAL_LANGUAGE_PATTERN``)
    est retiré du code langue et exposé via ``is_original``."""
    transcripts: list[LanguageTranscript] = []
    seen_languages: set[str] = set()

    prefix = f"{video_id}."
    for vtt_path in sorted(tmp_dir.glob(f"{video_id}*.vtt")):
        raw_lang = vtt_path.name[len(prefix) : -len(".vtt")]
        is_original = raw_lang.endswith("-orig")
        language = raw_lang[: -len("-orig")] if is_original else raw_lang

        if language in seen_languages:
            continue

        segments = _parse_vtt(vtt_path)
        if not segments:
            continue

        seen_languages.add(language)
        transcripts.append(
            LanguageTranscript(
                language=language,
                is_original=is_original,
                segmentations=segments,
                text=" ".join(segment.text for segment in segments),
            )
        )

    return transcripts


def _select_default_language(transcripts: list[LanguageTranscript], languages: list[str]) -> str:
    """Langue à afficher par défaut : la langue originale de la vidéo si dispo,
    sinon la première langue demandée trouvée (ordre de préférence), sinon
    n'importe quelle autre langue récupérée."""
    for transcript in transcripts:
        if transcript.is_original:
            return transcript.language
    available = {t.language for t in transcripts}
    for lang in languages:
        if lang in available:
            return lang
    return transcripts[0].language


def _clean_caption_text(text: str) -> str:
    text = _TAG_RE.sub("", text)
    return " ".join(text.split())


def _timestamp_to_seconds(timestamp: str) -> float:
    parts = [float(p) for p in timestamp.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    hours, minutes, seconds = parts
    return hours * 3600 + minutes * 60 + seconds


def _parse_vtt(path: Path) -> list[Segmentation]:
    """Parse un fichier VTT en segments. Les sous-titres auto-générés YouTube
    répètent souvent la même ligne sur plusieurs cues consécutifs (effet de
    défilement) : on ignore les doublons exacts consécutifs en best-effort."""
    segments: list[Segmentation] = []
    last_text: Optional[str] = None

    for caption in webvtt.read(str(path)):
        text = _clean_caption_text(caption.text)
        if not text or text == last_text:
            continue
        segments.append(
            Segmentation(
                start_time=_timestamp_to_seconds(caption.start),
                end_time=_timestamp_to_seconds(caption.end),
                label="transcription",
                confidence=None,
                text=text,
            )
        )
        last_text = text

    return segments
