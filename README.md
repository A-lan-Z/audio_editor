# TextAudio Edit

Local, single-user, audio-only MVP for transcript-driven audio editing.

MVP goals and scope are defined in `requirements.md` (with AI/workflow guidance in `AI.md`).

## Prerequisites

- Python 3.10+
- Node.js 18+

## Install

```bash
make install
```

Manual install:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
cd frontend && npm install
```

## Run (dev)

```bash
make dev
```

Manual run:

```bash
.venv/bin/python -m uvicorn backend.main:app --reload --port 8000
cd frontend && npm run dev
```

## Project structure

```
audio_editor/
├── backend/         # FastAPI app + services
├── frontend/        # Vite + React + TypeScript UI
├── tests/           # pytest (backend) + vitest (frontend)
├── scripts/         # developer utilities
├── docs/            # design notes
├── samples/         # synthetic samples only (no real user data)
└── .github/
```

## Docs & references

- `requirements.md`: product scope and requirements
- `AI.md`: AI behavior + coding guidelines
- `AGENTS.md`: repo conventions
- `WORKPLAN.md`: phased implementation plan
- `TASKBOARD.md`: task tracking + status

## Troubleshooting

- If `make dev` fails to bind ports, ensure nothing is running on `8000`/`5173` and that your environment permits local servers.
- If Python isn’t found as `python`, use `python3`.
- ASR models are downloaded/cached on first transcription. Set `TEXTAUDIO_MODELS_DIR` to control where models are stored (default: `./models/`, gitignored).
