# AI Audio Editor

Web-based audio editor where teams record separately and AI makes it sound like they were in the same room. Edit audio by editing text.

## Tech Stack

- **Frontend**: React 19 + TypeScript 5.7, Vite 6, TailwindCSS 4, TipTap 2 (transcript editor), wavesurfer.js 7 (waveform), Tone.js 15 (playback), FFmpeg.wasm 0.12 (format conversion)
- **Backend**: Python 3.12, FastAPI 0.115, Celery 5 + Redis 7 (job queue), SQLAlchemy 2 + Alembic (ORM/migrations), Supabase (auth + PostgreSQL 16 + S3 storage)
- **AI**: OpenAI Whisper API (transcription), OpenAI TTS API (voice generation/boundary smoothing)
- **Deploy**: Vercel (frontend), Railway (backend + workers), Supabase (DB + auth + storage)

## Commands

| Action     | Frontend (`/frontend`)          | Backend (`/backend`)              |
|------------|---------------------------------|-----------------------------------|
| Dev server | `npm run dev`                   | `uvicorn app.main:app --reload`   |
| Build      | `npm run build`                 | N/A                               |
| Lint       | `npm run lint`                  | `ruff check . && mypy .`         |
| Format     | `npm run format`                | `ruff format .`                   |
| Test       | `npm run test`                  | `pytest`                          |
| Migrate    | N/A                             | `alembic upgrade head`            |

## Directory Structure

```
frontend/           # React SPA (Vite)
  src/
    components/     # React components (PascalCase.tsx)
    hooks/          # Custom hooks (useCamelCase.ts)
    services/       # API client, audio engine (camelCase.ts)
    stores/         # Zustand stores (camelCase.ts)
    types/          # TypeScript types (camelCase.ts)
    pages/          # Route pages (PascalCase.tsx)
backend/            # FastAPI application
  app/
    api/            # Route handlers (snake_case.py)
    models/         # SQLAlchemy models (snake_case.py)
    schemas/        # Pydantic schemas (snake_case.py)
    services/       # Business logic (snake_case.py)
    workers/        # Celery tasks (snake_case.py)
  migrations/       # Alembic migrations
docs/               # Architecture, tasks, ADRs
```

## Code Style

- **Frontend**: Named exports, functional components, Zustand for state, `@/` path alias for `src/`. No default exports except pages. Prefer `interface` over `type` for object shapes.
- **Backend**: Type hints on all functions. Pydantic for all request/response schemas. Async endpoints. Dependency injection via FastAPI `Depends()`. No bare `except`.
- **Both**: No `any`/`Any` types without justification. Keep files under 300 lines.

## Boundaries

- Always: run tests before marking work complete, run lint, use feature branches
- Ask first: adding new dependencies, DB schema changes, changing API contracts, modifying deployment config
- Never: commit `.env` or secrets, edit CI/CD pipelines without approval, push directly to `main`, store API keys in code
