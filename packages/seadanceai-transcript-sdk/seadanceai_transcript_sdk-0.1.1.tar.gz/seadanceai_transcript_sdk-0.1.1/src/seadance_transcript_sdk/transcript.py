from __future__ import annotations

import time
from typing import List, Optional

import requests
from youtube_transcript_api import YouTubeTranscriptApi

from .constants import DEFAULT_LANGUAGE, DEFAULT_LANGUAGE_PROBE_ORDER, DEFAULT_TACTIQ_ENDPOINT, LANGUAGE_DISPLAY_NAMES, YOUTUBE_URL_PREFIX
from .types import LanguageOption, LanguagesResponse, TranscriptResponse, TranscriptSnippet


class TranscriptError(Exception):
  """Raised when both transcript sources fail."""


def get_transcript(video_id: str, language: str = DEFAULT_LANGUAGE, enable_fallback: bool = True, tactiq_endpoint: str = DEFAULT_TACTIQ_ENDPOINT, request_timeout: int = 15_000) -> TranscriptResponse:
  start = time.time()
  try:
    snippets = _fetch_from_tactiq(video_id, language, tactiq_endpoint, request_timeout)
    if not snippets and enable_fallback:
      raise TranscriptError("Primary source returned empty result")
    if snippets:
      return _build_response(video_id, language, "tactiq-primary", snippets, start)
  except Exception as primary_error:
    if not enable_fallback:
      raise
    fallback = _fetch_from_youtube(video_id, language)
    return _build_response(video_id, language, "youtube-transcript-api", fallback, start, primary_error)

  fallback = _fetch_from_youtube(video_id, language)
  return _build_response(video_id, language, "youtube-transcript-api", fallback, start, "Empty result from primary")


def detect_available_languages(video_id: str, candidate_languages: Optional[List[str]] = None, tactiq_endpoint: str = DEFAULT_TACTIQ_ENDPOINT, request_timeout: int = 8_000) -> LanguagesResponse:
  languages: List[LanguageOption] = []
  candidates = candidate_languages or DEFAULT_LANGUAGE_PROBE_ORDER

  for index in range(0, len(candidates), 4):
    batch = candidates[index:index + 4]
    for code in batch:
      try:
        snippets = _fetch_from_tactiq(video_id, code, tactiq_endpoint, request_timeout)
        if snippets and any(snippet.text.strip() for snippet in snippets):
          languages.append(LanguageOption(
            language_code=code,
            name=LANGUAGE_DISPLAY_NAMES.get(code, code.upper()),
            vss_id=code,
            is_translatable=True
          ))
      except Exception:
        pass
    if len(languages) >= 3:
      break
    if index + 4 < len(candidates):
      time.sleep(0.15)

  if not languages:
    languages.append(LanguageOption(language_code=DEFAULT_LANGUAGE, name=LANGUAGE_DISPLAY_NAMES.get(DEFAULT_LANGUAGE, "English"), vss_id=DEFAULT_LANGUAGE))

  return LanguagesResponse(languages=languages, video_id=video_id, count=len(languages))


def _fetch_from_tactiq(video_id: str, language: str, endpoint: str, request_timeout: int) -> List[TranscriptSnippet]:
  response = requests.post(
    endpoint,
    json={"langCode": language or DEFAULT_LANGUAGE, "videoUrl": f"{YOUTUBE_URL_PREFIX}{video_id}"},
    timeout=request_timeout / 1000 if request_timeout else None,
    headers={
      "Content-Type": "application/json",
      "User-Agent": "seadanceai-transcript-sdk/py"
    }
  )
  response.raise_for_status()
  data = response.json()
  captions = data.get("captions") or []
  snippets: List[TranscriptSnippet] = []
  for caption in captions:
    text = caption.get("text", "")
    start = float(caption.get("start") or caption.get("offset") or 0)
    duration = float(caption.get("dur") or caption.get("duration") or 0)
    snippets.append(TranscriptSnippet(text=text, start=start, duration=duration))
  return snippets


def _fetch_from_youtube(video_id: str, language: str) -> List[TranscriptSnippet]:
  api = YouTubeTranscriptApi()
  transcripts = api.get_transcript(f"{video_id}", languages=[language, DEFAULT_LANGUAGE])
  return [TranscriptSnippet(text=item.get("text", ""), start=float(item.get("start", 0)), duration=float(item.get("duration", 0))) for item in transcripts]


def _build_response(video_id: str, language: str, source: str, snippets: List[TranscriptSnippet], start: float, primary_error: Optional[Exception | str] = None) -> TranscriptResponse:
  elapsed = int((time.time() - start) * 1000)
  return TranscriptResponse(
    snippets=snippets,
    video_id=video_id,
    language=language,
    language_code=language,
    count=len(snippets),
    source=source,
    response_time_ms=elapsed,
    primary_error=str(primary_error) if primary_error else None
  )
