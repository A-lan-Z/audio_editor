# Agent Instructions — AI Audio Editor

## Architecture Pattern

This project uses a **layered architecture** on both frontend and backend:

### Backend (FastAPI): Route → Service → Repository
- **`api/`** (Routes): HTTP request handling, auth guards, input validation via Pydantic schemas. No business logic. Thin layer that calls services.
- **`services/`** (Business Logic): All domain logic lives here. Services are stateless, accept typed inputs, return typed outputs. Services call repositories for data access and external APIs for AI operations.
- **`models/`** (SQLAlchemy Models): Database table definitions. No methods beyond relationships and `__repr__`.
- **`schemas/`** (Pydantic): Request/response DTOs. Separate `Create`, `Update`, and `Response` schemas per entity.
- **`workers/`** (Celery Tasks): Long-running async jobs (transcription, normalization, export). Each task calls a service function — no inline business logic.

### Frontend (React): Page → Component → Hook → Service
- **`pages/`**: Top-level route components. Compose feature components. Handle route params.
- **`components/`**: Reusable UI. Accept props, emit callbacks. No direct API calls — use hooks.
- **`hooks/`**: Custom hooks encapsulate state logic and side effects. Call services for data.
- **`services/`**: API client functions (fetch wrappers), audio engine abstractions. Pure functions or classes.
- **`stores/`**: Zustand stores for shared state (project, editor, playback). Keep stores focused — one per domain.

## Testing Strategy

### Unit Tests
- **Backend**: Test each service function in isolation. Mock external dependencies (DB, OpenAI, storage). Use `pytest` + `pytest-asyncio`. Aim for >80% coverage on services.
- **Frontend**: Test hooks and utility functions with Vitest. Test components with React Testing Library. Mock API calls with MSW.

### Integration Tests
- **Backend**: Test API routes end-to-end using `httpx.AsyncClient` with a test database. Test Celery tasks with eager mode.
- **Frontend**: Test full user flows (upload → transcription → edit → export) with Playwright.

### What NOT to Test
- SQLAlchemy model definitions (tested implicitly via integration tests)
- Pydantic schemas (validated by type system)
- Third-party library internals

## Error Handling

### Backend
- Raise `HTTPException` with appropriate status codes in route handlers only.
- Services raise domain-specific exceptions (e.g., `ProjectNotFoundError`, `TranscriptionFailedError`) defined in `app/exceptions.py`.
- Route handlers catch domain exceptions and map to HTTP responses.
- All Celery tasks must catch exceptions, update job status to `failed`, and log the error. Never let a task silently fail.
- Use structured logging (`structlog`) with request_id correlation.

### Frontend
- API errors are caught in service functions and thrown as typed errors.
- Components use error boundaries for render errors.
- Async operations use toast notifications for user-facing errors.
- Never swallow errors silently. Log to console in dev, to a service in production.

## File Naming Conventions

| Location          | Convention      | Example                        |
|-------------------|-----------------|--------------------------------|
| React components  | PascalCase.tsx  | `TranscriptEditor.tsx`         |
| React hooks       | useCamelCase.ts | `usePlayback.ts`               |
| React pages       | PascalCase.tsx  | `ProjectPage.tsx`              |
| Zustand stores    | camelCase.ts    | `editorStore.ts`               |
| TS services       | camelCase.ts    | `audioEngine.ts`               |
| TS types          | camelCase.ts    | `project.ts`                   |
| Python modules    | snake_case.py   | `audio_processing.py`          |
| Alembic migrations| auto-generated  | `001_create_projects_table.py` |
| Test files        | test_*.py / *.test.ts | `test_project_service.py` |

## Key Conventions

- **IDs**: Use UUIDs everywhere (database, API, frontend state).
- **Timestamps**: Store as UTC `datetime` in DB, return as ISO 8601 strings in API, display in user's local timezone on frontend.
- **Audio references**: Never copy audio data. Use `(file_id, start_time, end_time)` tuples to reference segments of original files.
- **Non-destructive editing**: The edit state is a playlist of segment references. Original audio files are immutable after upload.
- **API versioning**: All endpoints under `/api/v1/`. No breaking changes without version bump.
- **Environment config**: All secrets and config via environment variables. Use `.env` files locally (never committed). Pydantic `Settings` class for backend config.
