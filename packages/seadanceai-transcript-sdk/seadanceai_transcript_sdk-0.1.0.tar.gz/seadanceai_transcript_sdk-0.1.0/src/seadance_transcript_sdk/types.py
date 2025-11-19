from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TranscriptSnippet:
  text: str
  start: float
  duration: float


@dataclass
class TranscriptResponse:
  snippets: List[TranscriptSnippet]
  video_id: str
  language: str
  language_code: str
  count: int
  source: str
  response_time_ms: int
  primary_error: Optional[str] = None


@dataclass
class LanguageOption:
  language_code: str
  name: str
  vss_id: str
  is_translatable: bool = True


@dataclass
class LanguagesResponse:
  languages: List[LanguageOption]
  video_id: str
  count: int


@dataclass
class TranscriptFormatResult:
  content: str
  filename: str
  mime_type: str


@dataclass
class SummaryQuestion:
  question: str
  answer: str
  timestamp: Optional[str] = None


@dataclass
class SummaryResult:
  summary: str
  key_points: List[str] = field(default_factory=list)
  top_questions: List[SummaryQuestion] = field(default_factory=list)
  duration_seconds: int = 0
