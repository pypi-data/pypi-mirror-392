from __future__ import annotations

from typing import Iterable, List

from .types import SummaryQuestion, SummaryResult, TranscriptResponse


def summarize_transcript(transcript: TranscriptResponse, title: str | None = None) -> SummaryResult:
  snippets = transcript.snippets
  if not snippets:
    return SummaryResult(summary="No transcript available.")

  full_text = " ".join(snippet.text for snippet in snippets)
  sentences = [sentence.strip() for sentence in full_text.split('.') if len(sentence.strip()) > 10]

  interval = max(1, len(sentences) // 5) if sentences else 1
  key_sentences: List[str] = []
  keywords = ["important", "key", "main", "first", "second", "finally", "conclusion", "summary"]
  for idx, sentence in enumerate(sentences):
    lower = sentence.lower()
    if any(keyword in lower for keyword in keywords) or idx % interval == 0:
      key_sentences.append(sentence)
    if len(key_sentences) >= 8:
      break

  summary_text = ". ".join(key_sentences) + "." if key_sentences else full_text[:200] + "..."
  key_points = _extract_key_points(snippets)
  questions = _build_top_questions(title or f"YouTube Video {transcript.video_id}")
  duration = _estimate_duration(snippets)

  return SummaryResult(summary=summary_text.strip(), key_points=key_points, top_questions=questions, duration_seconds=duration)


def _extract_key_points(snippets: Iterable) -> List[str]:
  snippets = list(snippets)
  if not snippets:
    return ["No key points available"]

  interval = max(1, len(snippets) // 6)
  points: List[str] = []
  for index in range(0, len(snippets), interval):
    text = snippets[index].text.strip()
    if len(text) > 15:
      snippet = text[:120] + ("..." if len(text) > 120 else "")
      points.append(snippet)
  return points or ["Key points derived from transcript"]


def _build_top_questions(title: str) -> List[SummaryQuestion]:
  lower_title = title.lower()
  return [
    SummaryQuestion(question=f"What is the main topic of '{title}'?", answer=f"This video covers {lower_title} with practical insights.", timestamp="00:00"),
    SummaryQuestion(question="What are the key takeaways?", answer="The video provides actionable information for viewers.", timestamp="00:30"),
    SummaryQuestion(question="Who should watch this video?", answer="Anyone interested in the subject discussed in the video.", timestamp="01:00")
  ]


def _estimate_duration(snippets: List) -> int:
  if not snippets:
    return 0
  last = snippets[-1]
  return int(round(last.start + last.duration))
