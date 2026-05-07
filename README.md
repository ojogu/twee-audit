# Tweet Audit

A Python CLI that uses Google Gemini to scan your X (Twitter) archive and flag posts that violate platform policies or personal brand guidelines.

---

## The Problem

Public-facing accounts accumulate thousands of posts over years. Manually reviewing that history for policy violations or reputational risks is impractical at scale.

Tweet Audit automates this: you point it at your X data archive, and it returns a prioritized list of posts to review and delete.

---

## Key Features

- **AI-Powered Content Analysis** — Sends each tweet to Google Gemini for evaluation against customizable moderation criteria
- **Customizable Moderation Rules** — Configurable forbidden keywords, tone standards, and content policies via system prompt
- **Checkpoint-Enabled Batch Processing** — Resumable processing prevents API quota waste if interrupted; tracks progress per batch
- **Checkpoint Persistence** — Saves progress to disk, enabling recovery without re-processing already-analyzed tweets
- **Dual-Mode CLI** — Separate commands for extraction (`extract-tweets`) and analysis (`analyze-tweets`); each returns structured exit codes
- **Resilient JSON Cleaning** — Multi-stage parser cleans Gemini's markdown-wrapped responses before Pydantic validation
- **Context-Managed File I/O** — Checkpoint and CSV writers use Python context managers for deterministic open/close and flush behavior
- **Comprehensive Test Suite** — Unit tests with mocked API responses cover happy paths, error types, and corrupted checkpoint scenarios

---

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Language | Python 3.12+ | Ecosystem for AI/ML tasks; readability |
| AI Model | Google Gemini (`google-genai`) | Direct model access with system instructions |
| Data Validation | Pydantic | Enforces schemas at every parsing boundary |
| Configuration | `pydantic-settings` | Environment-based config with `.env` support |
| Logging | `rich` | Human-readable console + structured file logs |
| Testing | pytest + `pytest-asyncio` | Async test support; parameterized error cases |

---

## System Architecture

```
tweets.json (X archive export)
       │
       ▼
┌──────────────┐
│ extract-tweets │
│  (JSON → CSV) │
└──────────────┘
       │
       ▼
extracted_tweets.csv
       │
       ▼
┌──────────────┐     ┌─────────────────┐
│ analyze-tweets│────▶│ Gemini API      │
│ (batch loop) │     │ + retry/backoff │
└──────────────┘     └─────────────────┘
       │                    │
       ▼                    ▼
┌──────────────┐     analyzed_tweets.csv
│ Checkpoint   │     (tweet_url, deleted)
│ (index saved)│
└──────────────┘
```

**Flow:** `extract-tweets` converts your X archive JSON into a flat CSV. `analyze-tweets` reads that CSV in configurable batches, sends each tweet to Gemini, validates the response via Pydantic, and writes flagged URLs to the output CSV. A checkpoint file tracks the last processed index so partial runs resume without waste.

See [docs/TRADEOFFS.md](docs/TRADEOFFS.md) for architectural trade-off rationale.

---

## Getting Started

### Prerequisites

- Python 3.12+
- A Google Cloud account with the Gemini API enabled
- Your X (Twitter) data archive as a JSON file (format: `[{ "tweet": { "id_str": "...", "full_text": "..." } }]`)

### Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/ojogu/twee-audit.git
cd twee-audit/tweet-audit

# 2. Install dependencies
uv sync

# 3. Create and populate .env
cp .env.example .env
# Edit .env: set GOOGLE_API_KEY and MODEL_NAME

# 4. Place your tweet archive
# Copy your tweets.json to data/tweets.json

# 5. Run extraction (one-time)
python -m src.cli extract-tweets

# 6. Run analysis
python -m src.cli analyze-tweets
```

### Access Points

| Output | File |
|---|---|
| Extracted tweets | `data/extracted_tweets.csv` |
| Flagged tweets | `data/analyzed_tweets.csv` |
| Checkpoint | `data/checkpoint.txt` |
| Application logs | `logs/` |

---

## Project Structure

```
tweet-audit/
├── src/
│   ├── ai_setup.py       # Gemini client, retry decorator, analysis loop
│   ├── cli.py            # argparse entrypoint
│   ├── config.py         # pydantic-settings, rich logging setup
│   ├── parser.py         # JSON/CSV readers, checkpoint context manager
│   ├── prompt.py         # Gemini system prompt (moderation criteria)
│   ├── schema.py         # Pydantic models for all data shapes
│   ├── service.py        # AuditService: orchestrates extraction + analysis
│   └── utils.py          # Directory/file creation, JSON cleaner
├── test/
│   ├── conftest.py       # Shared pytest fixtures
│   ├── test_ai_setup.py  # API client tests with mocked responses
│   ├── test_cli.py       # CLI error propagation tests
│   └── test_parser.py    # Checkpoint, CSV, JSON parsing tests
└── docs/
    └── TRADEOFFS.md       # Architectural decisions and rationale
```

---

## Development Commands

```bash
uv run pytest           # Run full test suite
uv run pytest -v        # Run with verbose output
```

---

## Engineering Challenges

**API Reliability** — The Gemini API is rate-limited and can return 429/503 errors at scale. The `retry_with_backoff` decorator in `ai_setup.py` detects retryable keywords and applies exponential backoff (1s × 2^attempt + jitter) to avoid compounding the problem. Max retries are capped to prevent infinite loops during extended outages.

**Checkpoint Integrity** — A corrupted checkpoint file (e.g., non-integer content) would cause the batch loop to crash or re-process tweets. The `Checkpoint.load()` method validates the file contents and raises a descriptive `ValueError` if the checkpoint is corrupted, preventing silent data corruption. Tests verify this behavior in `test_parser.py`.

See [docs/TRADEOFFS.md](docs/TRADEOFFS.md) for the full rationale behind batch sizing, fail-fast error handling, and schema validation strategy.

---

## Contact

Built by [ojogu](https://github.com/ojogu). Open an issue for bugs or feature requests.
