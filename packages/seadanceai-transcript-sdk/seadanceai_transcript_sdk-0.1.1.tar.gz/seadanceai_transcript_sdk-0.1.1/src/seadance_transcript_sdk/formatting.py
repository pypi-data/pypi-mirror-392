from __future__ import annotations

from .types import TranscriptFormatResult, TranscriptResponse

MIME_TYPES = {
  "txt": "text/plain; charset=utf-8",
  "srt": "application/x-subrip",
  "vtt": "text/vtt"
}


def format_transcript(transcript: TranscriptResponse, fmt: str = "txt") -> str:
  fmt = fmt.lower()
  if fmt == "srt":
    return _format_srt(transcript)
  if fmt == "vtt":
    return _format_vtt(transcript)
  return _format_txt(transcript)


def format_transcript_file(transcript: TranscriptResponse, fmt: str = "txt") -> TranscriptFormatResult:
  fmt = fmt.lower()
  content = format_transcript(transcript, fmt)
  filename = f"transcript-{transcript.video_id}.{fmt}"
  mime_type = MIME_TYPES.get(fmt, MIME_TYPES["txt"])
  return TranscriptFormatResult(content=content, filename=filename, mime_type=mime_type)


def _pad(value: int, size: int = 2) -> str:
  return str(value).zfill(size)


def _format_timestamp(seconds: float) -> str:
  hours = int(seconds // 3600)
  minutes = int((seconds % 3600) // 60)
  secs = int(seconds % 60)
  millis = int((seconds % 1) * 1000)
  return f"{_pad(hours)}:{_pad(minutes)}:{_pad(secs)},{_pad(millis, 3)}"


def _format_srt(transcript: TranscriptResponse) -> str:
  lines = []
  for index, snippet in enumerate(transcript.snippets, start=1):
    start = _format_timestamp(snippet.start)
    end = _format_timestamp(snippet.start + snippet.duration)
    lines.append(f"{index}\n{start} --> {end}\n{snippet.text}\n")
  return "\n".join(lines).strip()


def _format_vtt(transcript: TranscriptResponse) -> str:
  entries = []
  for snippet in transcript.snippets:
    start = _format_timestamp(snippet.start)
    end = _format_timestamp(snippet.start + snippet.duration)
    entries.append(f"{start} --> {end}\n{snippet.text}")
  return "WEBVTT\n\n" + "\n\n".join(entries)


def _format_txt(transcript: TranscriptResponse) -> str:
  return "\n".join(snippet.text for snippet in transcript.snippets)
