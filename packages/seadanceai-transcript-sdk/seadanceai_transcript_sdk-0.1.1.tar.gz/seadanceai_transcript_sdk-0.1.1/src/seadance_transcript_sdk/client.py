from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .formatting import format_transcript, format_transcript_file
from .summary import summarize_transcript
from .transcript import detect_available_languages, get_transcript
from .types import LanguagesResponse, SummaryResult, TranscriptFormatResult, TranscriptResponse


@dataclass
class TranscriptClient:
  enable_fallback: bool = True
  tactiq_endpoint: str | None = None

  def get_transcript(self, video_id: str, language: str = "en", *, enable_fallback: Optional[bool] = None) -> TranscriptResponse:
    return get_transcript(video_id, language=language, enable_fallback=self._resolve_fallback(enable_fallback), tactiq_endpoint=self.tactiq_endpoint or None)

  def detect_languages(self, video_id: str) -> LanguagesResponse:
    return detect_available_languages(video_id)

  def summarize(self, transcript: TranscriptResponse, title: str | None = None) -> SummaryResult:
    return summarize_transcript(transcript, title=title)

  def format(self, transcript: TranscriptResponse, fmt: str = "txt") -> str:
    return format_transcript(transcript, fmt)

  def format_to_file(self, transcript: TranscriptResponse, fmt: str = "txt") -> TranscriptFormatResult:
    return format_transcript_file(transcript, fmt)

  def _resolve_fallback(self, override: Optional[bool]) -> bool:
    return self.enable_fallback if override is None else override
