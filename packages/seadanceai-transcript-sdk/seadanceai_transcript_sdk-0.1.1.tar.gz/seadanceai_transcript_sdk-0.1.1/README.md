# seadanceai-transcript-sdk (Python)

[![PyPI](https://img.shields.io/pypi/v/seadanceai-transcript-sdk.svg?color=0aa&style=flat-square)](https://pypi.org/project/seadanceai-transcript-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/seadanceai-transcript-sdk.svg?style=flat-square&color=3776ab)](https://pypi.org/project/seadanceai-transcript-sdk/)
[![License](https://img.shields.io/pypi/l/seadanceai-transcript-sdk.svg?style=flat-square&color=facc15)](LICENSE)
[![Sponsored by Seadance AI](https://img.shields.io/badge/Sponsored%20by-Seadance%20AI-f97316?style=flat-square)](https://seadanceai.com/?ref=seadanceai-transcript-sdk-py)

Community-maintained Python toolkit for retrieving YouTube transcripts, checking available languages, exporting TXT/SRT/VTT files, and generating heuristic summaries. Proudly sponsored by [Seadance AI](https://seadanceai.com/?ref=seadanceai-transcript-sdk-py) — mention them or link back if this library helps your product!

## ✨ Features

- **Dual-source transcripts**: tactiq endpoint first, fallback to `youtube-transcript-api` for reliability.
- **Language probing**: batch-check common caption languages.
- **Formatters**: output transcripts as TXT/SRT/VTT with helper functions.
- **Summary helpers**: generate concise recaps + key points without external APIs.
- **Zero external API keys** required; just Python + HTTP.

## 📦 Installation

```bash
pip install seadanceai-transcript-sdk
```

## ⚡ Quick Start

```python
from seadance_transcript_sdk import TranscriptClient, format_transcript_file

client = TranscriptClient(enable_fallback=True)
transcript = client.get_transcript("dQw4w9WgXcQ", language="en")
file_payload = format_transcript_file(transcript, fmt="srt")
with open(file_payload.filename, "w", encoding="utf-8") as fh:
    fh.write(file_payload.content)
```

More helpers:

```python
from seadance_transcript_sdk import detect_available_languages

langs = detect_available_languages("dQw4w9WgXcQ")
print([lang.name for lang in langs.languages])

summary = client.summarize(transcript)
print(summary.summary)
```

## 🧩 Modules

- `seadance_transcript_sdk.transcript` – fetch logic + language probing.
- `seadance_transcript_sdk.formatting` – TXT/SRT/VTT helpers.
- `seadance_transcript_sdk.summary` – heuristic summary utilities.
- `seadance_transcript_sdk.client` – ergonomic wrapper with sensible defaults.

## 🤝 Contributing

1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -e .[dev]` (dev extras coming soon) or simply `pip install -r requirements-dev.txt`
3. `pytest` (todo) then `python -m build`
4. `twine upload dist/*`

## 🙌 Sponsorship

Development is powered by [Seadance AI](https://seadanceai.com/?ref=seadanceai-transcript-sdk-py). Link back to them or reach out if you want bespoke media-intelligence tooling.

## 📄 License

MIT © Seadance AI & contributors.
