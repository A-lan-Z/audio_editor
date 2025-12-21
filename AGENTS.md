# Repository Guidelines

Contributor guide for TextAudio Edit. Use this alongside `requirements.md` and `AI.md`, which define scope and AI behavior. Keep changes local-first and aligned with the MVP: single-user, audio-only, transcript-driven editing.

## Project Structure & Module Organization
- Current state: docs at the repo root (`requirements.md`, `AI.md`). Create `docs/` for future design notes and `samples/` for small synthetic audio/text only.
- Proposed code layout: `backend/` for API and audio services, `frontend/` for the transcript UI, `scripts/` for utilities, and `tests/` mirroring package structure.
- Keep data, models, and generated assets out of version control; use `.gitignore` entries for audio exports and local model weights.

## Build, Test, and Development Commands
- Prefer a `Makefile` or `npm scripts` that wrap common tasks. Examples to standardize when code lands:
  - Backend (Python/FastAPI assumed): `python -m venv .venv && source .venv/bin/activate`, `pip install -r requirements.txt`, run dev server with `uvicorn backend.main:app --reload`.
  - Frontend (Vite/React assumed): `npm install`, `npm run dev` for local UI.
  - Unified helpers: `make fmt` (format), `make lint`, `make test`, `make dev` (launch both services).

## Coding Style & Naming Conventions
- Python: 4-space indent, type hints required; run `ruff`/`black` before committing.
- TypeScript/JavaScript: use `eslint` + `prettier`; default to named exports for modules, `PascalCase` for components, `camelCase` for variables/functions.
- Keep audio/time logic documented with short comments; avoid silent magic numbers.

## Testing Guidelines
- Use `pytest` for backend (name files `test_*.py`) and `vitest`/React Testing Library for frontend (`*.test.ts(x)`).
- Cover transcript-to-audio mapping, edit operations, and error handling; add regression tests for any audio alignment or synthesis fixes.
- Run full suite (`make test` or `npm test`/`pytest`) before PRs; add fixtures with synthetic audio/transcripts only.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`). Keep messages scoped and descriptive.
- PRs should link issues, summarize behavior changes, list test commands executed, and include screenshots/GIFs for UI tweaks.
- Call out deviations from `requirements.md` or experimental work in the PR description; keep feature creep explicitly flagged.

## Security & Configuration Notes
- Do not commit real user audio or transcripts; prefer generated or anonymized samples.
- Default to local processing; avoid cloud dependencies unless explicitly approved and documented with rationale.
