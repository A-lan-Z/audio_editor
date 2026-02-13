# Implementation Tasks — AI Audio Editor

## Phase 1: Foundation

> Project scaffolding, configuration, database, and basic infrastructure. No features yet.

### T1.1 — Initialize frontend project
**Files**: `frontend/package.json`, `frontend/vite.config.ts`
**Do**: Scaffold Vite + React 19 + TypeScript project. Install TailwindCSS 4. Configure path alias `@/` → `src/`. Add ESLint + Prettier config.
**Acceptance**: `npm run dev` serves a blank page. `npm run lint` passes. `npm run build` succeeds.

### T1.2 — Initialize backend project
**Files**: `backend/pyproject.toml`, `backend/app/main.py`
**Do**: Create Python project with FastAPI, uvicorn, SQLAlchemy 2, alembic, celery, redis, pydantic-settings. Configure ruff + mypy. Create `app/main.py` with health check endpoint.
**Acceptance**: `uvicorn app.main:app --reload` serves `GET /health` → `{"status": "ok"}`. `ruff check .` and `mypy .` pass.

### T1.3 — Configure Supabase integration
**Files**: `backend/app/config.py`, `backend/app/dependencies.py`
**Do**: Create Pydantic `Settings` class loading env vars for Supabase URL, anon key, service key, DB connection string, Redis URL, OpenAI key. Create DB engine factory and session dependency.
**Acceptance**: `Settings` loads from `.env.example`. DB session dependency can be injected into a test route.

### T1.4 — Database models and initial migration
**Files**: `backend/app/models/project.py`, `backend/app/models/speaker.py`, `backend/app/models/audio_file.py`, `backend/app/models/segment.py`, `backend/app/models/edit_state.py`, `backend/app/models/export.py`, `backend/app/models/job.py`
**Do**: Define all SQLAlchemy models per the data model in ARCHITECTURE.md. Create Alembic initial migration.
**Acceptance**: `alembic upgrade head` creates all tables. `alembic downgrade base` drops them. Models match the ER diagram.
**Depends on**: T1.3

### T1.5 — Auth middleware
**Files**: `backend/app/middleware/auth.py`, `backend/app/dependencies.py`
**Do**: Create FastAPI middleware/dependency that verifies Supabase JWT from `Authorization: Bearer <token>` header. Extract user ID. Create `get_current_user` dependency.
**Acceptance**: Protected route returns 401 without token, 200 with valid Supabase token.
**Depends on**: T1.3

### T1.6 — Frontend auth flow
**Files**: `frontend/src/services/supabase.ts`, `frontend/src/hooks/useAuth.ts`, `frontend/src/pages/LoginPage.tsx`
**Do**: Initialize Supabase client. Create `useAuth` hook (login, signup, logout, session). Create login page with email auth. Set up auth context/provider. Add authenticated route wrapper.
**Acceptance**: User can sign up, log in, log out. Auth token is sent with API requests. Unauthenticated users are redirected to login.
**Depends on**: T1.1

### T1.7 — API client setup
**Files**: `frontend/src/services/api.ts`
**Do**: Create typed fetch wrapper that attaches Supabase auth token, handles errors, and provides typed request/response functions for all API endpoints.
**Acceptance**: API client correctly attaches auth headers. Type-safe wrappers exist for all planned endpoints (can return mock data initially).
**Depends on**: T1.6

### T1.8 — Frontend routing and layout shell
**Files**: `frontend/src/App.tsx`, `frontend/src/pages/DashboardPage.tsx`, `frontend/src/pages/ProjectPage.tsx`, `frontend/src/components/Layout.tsx`
**Do**: Set up React Router with routes: `/login`, `/dashboard`, `/projects/:id`. Create layout shell with navigation. Dashboard shows empty project list. Project page is a placeholder.
**Acceptance**: Navigation between pages works. Layout renders consistently. Protected routes redirect to login.
**Depends on**: T1.6

---

## Phase 2: Core — Upload & Transcription Pipeline

> The critical path: upload audio → transcribe → display script-style transcript.

### T2.1 — Project CRUD API
**Files**: `backend/app/api/projects.py`, `backend/app/services/project_service.py`
**Do**: Implement POST/GET/PATCH/DELETE for projects. Service layer handles business logic. Route layer handles auth and validation.
**Acceptance**: All CRUD operations work via API. Users can only access their own projects. Tests pass.
**Depends on**: T1.4, T1.5

### T2.2 — Project list and creation UI
**Files**: `frontend/src/pages/DashboardPage.tsx`, `frontend/src/components/ProjectCard.tsx`, `frontend/src/stores/projectStore.ts`
**Do**: Dashboard displays user's projects as cards. "New Project" button opens creation dialog (name + voice consent checkbox). Zustand store for project state.
**Acceptance**: User can create a project and see it in the list. Clicking a project navigates to `/projects/:id`.
**Depends on**: T1.7, T1.8, T2.1

### T2.3 — Speaker management API
**Files**: `backend/app/api/speakers.py`, `backend/app/services/speaker_service.py`
**Do**: Implement POST/PATCH/DELETE for speakers within a project.
**Acceptance**: Speakers can be created, renamed, and deleted. Speaker belongs to project. Proper 404/403 handling.
**Depends on**: T2.1

### T2.4 — Speaker management UI
**Files**: `frontend/src/components/SpeakerPanel.tsx`, `frontend/src/components/SpeakerForm.tsx`
**Do**: Panel on project page showing speakers. Add/edit/delete speakers. Each speaker shows name and upload status.
**Acceptance**: User can add speakers to a project, rename them, and remove them.
**Depends on**: T2.2, T2.3

### T2.5 — Audio upload API with storage
**Files**: `backend/app/api/upload.py`, `backend/app/services/storage_service.py`, `backend/app/services/audio_file_service.py`
**Do**: Multipart upload endpoint. Store original file in Supabase Storage. Create `AudioFile` record. Validate file type and size (max 500MB).
**Acceptance**: File uploads to Supabase Storage. AudioFile record created with correct metadata. Rejects invalid formats and oversized files.
**Depends on**: T2.3

### T2.6 — Client-side FFmpeg conversion + upload UI
**Files**: `frontend/src/services/audioConverter.ts`, `frontend/src/components/AudioUploader.tsx`
**Do**: Initialize FFmpeg.wasm. Convert uploaded files to WAV before sending to backend. Show conversion progress. Upload with progress bar. Drag-and-drop support.
**Acceptance**: User can drag-and-drop or click to upload MP3/M4A/FLAC/OGG/WEBM files. Files are converted to WAV in browser. Upload progress is visible.
**Depends on**: T2.4, T2.5

### T2.7 — Transcription worker
**Files**: `backend/app/workers/transcription.py`, `backend/app/services/transcription_service.py`
**Do**: Celery task that downloads audio from storage, sends to OpenAI Whisper API with word-level timestamps, creates `Segment` records with word data, updates job status.
**Acceptance**: Queuing a transcription job produces segments with word-level timestamps. Job status transitions: queued → processing → completed. Failed jobs are marked with error info.
**Depends on**: T2.5, T1.4

### T2.8 — Transcription API and job polling
**Files**: `backend/app/api/transcription.py`, `backend/app/api/jobs.py`, `backend/app/services/job_service.py`
**Do**: POST to start transcription. GET transcript segments. GET job status. Job list for project.
**Acceptance**: Transcription can be started, polled for status, and segments retrieved when complete.
**Depends on**: T2.7

### T2.9 — Transcript display (read-only)
**Files**: `frontend/src/components/TranscriptViewer.tsx`, `frontend/src/stores/transcriptStore.ts`
**Do**: Render segments in script-style format (`SPEAKER: text`). Word-level spans for click targeting. Poll for transcription job completion. Loading state while transcribing.
**Acceptance**: After transcription completes, transcript displays in script format. Each word is a clickable span. Speakers are visually distinct.
**Depends on**: T2.8, T2.4

### T2.10 — Click-to-listen
**Files**: `frontend/src/services/audioEngine.ts`, `frontend/src/hooks/usePlayback.ts`
**Do**: Initialize Tone.js audio context. Load audio file chunks. When user clicks a word, play audio from that word's start timestamp. Highlight currently-playing word.
**Acceptance**: Clicking any word in the transcript plays the audio from that point. Currently-playing word is highlighted. Playback can be stopped.
**Depends on**: T2.9

---

## Phase 3: Features — Editing, Normalization, Playback, Export

> The editing experience, audio processing, and output pipeline.

### T3.1 — TipTap transcript editor setup
**Files**: `frontend/src/components/TranscriptEditor.tsx`, `frontend/src/components/extensions/speakerBlock.ts`
**Do**: Replace read-only viewer with TipTap editor. Custom `SpeakerBlock` node extension that renders `SPEAKER: text` blocks. Each word maps to a segment/word reference via node attributes. Support text selection across words.
**Acceptance**: Transcript renders in TipTap with speaker blocks. Text is selectable. Speaker labels are non-editable but text content is editable.
**Depends on**: T2.9

### T3.2 — Edit state management
**Files**: `frontend/src/stores/editorStore.ts`, `frontend/src/services/editStateService.ts`
**Do**: Zustand store for edit state (ordered segment entries with trim offsets). Sync with backend via PUT. Optimistic locking (version field). Derive edit state changes from TipTap operations (delete, reorder).
**Acceptance**: Editing text in TipTap updates the edit state. Edit state persists to backend. Version conflicts are detected.
**Depends on**: T3.1, T2.8 (for initial edit state from segments)

### T3.3 — Delete and trim operations
**Files**: `frontend/src/components/TranscriptEditor.tsx` (extend), `frontend/src/stores/editorStore.ts` (extend)
**Do**: Selecting text and pressing delete removes those words from the edit state (adjusts trim offsets or removes entries). Trim: select a range → "Keep only this" action. Update edit state accordingly.
**Acceptance**: User can delete words/sentences. Deleted text disappears from transcript. Edit state reflects deletions. Trim keeps only selected audio.
**Depends on**: T3.2

### T3.4 — Reorder segments (drag-and-drop)
**Files**: `frontend/src/components/TranscriptEditor.tsx` (extend), `frontend/src/components/DragHandle.tsx`
**Do**: Speaker blocks can be reordered via drag-and-drop. Update edit state entry order. Visual feedback during drag.
**Acceptance**: User can drag speaker blocks to reorder. Edit state updates with new order. Undo reverts to previous order.
**Depends on**: T3.2

### T3.5 — Undo/redo
**Files**: `frontend/src/stores/editorStore.ts` (extend), `backend/app/api/edit_state.py`
**Do**: Client-side undo/redo stack (snapshot edit state on each change). Keyboard shortcuts (Ctrl+Z / Ctrl+Shift+Z). Sync undo/redo stacks to backend.
**Acceptance**: Undo reverts the last edit. Redo reapplies it. Stack persists across page reloads.
**Depends on**: T3.2

### T3.6 — Transcript text correction
**Files**: `frontend/src/components/TranscriptEditor.tsx` (extend), `backend/app/api/transcription.py` (extend)
**Do**: Double-click a word to edit its text (correct transcription errors). PATCH segment with corrected text. Audio mapping remains unchanged — only display text changes.
**Acceptance**: User can correct misheard words. Changes persist. Audio-text mapping is unaffected (clicking still plays original audio).
**Depends on**: T3.1

### T3.7 — Normalization worker
**Files**: `backend/app/workers/normalization.py`, `backend/app/services/normalization_service.py`
**Do**: Celery task that processes each speaker's audio: loudness normalization (LUFS targeting), basic EQ, noise reduction (via `noisereduce` library), dynamic range compression. Store normalized audio file. Use `pydub` or `librosa`.
**Acceptance**: Normalization job produces a new audio file with consistent loudness, reduced noise, and balanced EQ. Original file is untouched.
**Depends on**: T2.5

### T3.8 — Per-speaker normalization controls
**Files**: `frontend/src/components/NormalizationPanel.tsx`, `backend/app/api/speakers.py` (extend)
**Do**: UI panel per speaker with sliders for: volume, EQ (bass/mid/treble), noise reduction strength, reverb removal, compression. Save settings via PATCH speaker. Re-run normalization with new settings.
**Acceptance**: User can adjust normalization settings per speaker. Changes trigger re-normalization. Before/after preview is available.
**Depends on**: T3.7, T2.4

### T3.9 — Continuous playback engine
**Files**: `frontend/src/services/audioEngine.ts` (extend), `frontend/src/hooks/usePlayback.ts` (extend), `frontend/src/components/PlaybackControls.tsx`
**Do**: Play through the entire edit state sequentially: load segments in order, pre-buffer next segment for gapless transitions, show playback position in transcript (highlight current word). Play/pause/stop controls. Scrub bar.
**Acceptance**: Full project plays back in edited order. Transitions between segments are gapless. Current position is tracked in the transcript. Standard playback controls work.
**Depends on**: T2.10, T3.2

### T3.10 — Waveform viewer
**Files**: `frontend/src/components/WaveformViewer.tsx`, `frontend/src/hooks/useWaveform.ts`
**Do**: Collapsible waveform display using wavesurfer.js. Synced with playback position. Shows segment boundaries. Click to seek. Optional — transcript is primary, waveform is secondary.
**Acceptance**: Waveform renders for current audio. Playback position syncs with waveform cursor. Segment boundaries are visible. Panel can be collapsed.
**Depends on**: T3.9

### T3.11 — AI boundary smoothing worker
**Files**: `backend/app/workers/smoothing.py`, `backend/app/services/smoothing_service.py`
**Do**: Celery task that takes two adjacent segment edges, extracts boundary audio, uses OpenAI TTS to regenerate a short transition (using voice profile), blends with crossfade. Store smoothed boundary audio.
**Acceptance**: Smoothed boundaries sound natural. Fallback to simple crossfade if AI generation fails. Job status is tracked.
**Depends on**: T3.7 (needs normalized audio)

### T3.12 — Export worker
**Files**: `backend/app/workers/export.py`, `backend/app/services/export_service.py`
**Do**: Celery task that reads edit state, assembles segments in order, applies normalization, inserts smoothed boundaries, renders to MP3 or WAV using `pydub`/`ffmpeg`. Upload to Supabase Storage.
**Acceptance**: Export produces a single audio file combining all speakers in edited order. Normalization is applied. Format is correct (MP3 or WAV). File is downloadable.
**Depends on**: T3.11, T3.7

### T3.13 — Export UI
**Files**: `frontend/src/components/ExportPanel.tsx`, `frontend/src/pages/ProjectPage.tsx` (extend)
**Do**: Export button with format selection (MP3/WAV). Shows export job progress. Download link when complete. Export history list.
**Acceptance**: User can trigger export, see progress, and download the result. Multiple exports are listed.
**Depends on**: T3.12, T2.8 (job polling)

---

## Phase 4: Polish

> Error handling, loading states, UX improvements, and production readiness.

### T4.1 — Global error handling and toast notifications
**Files**: `frontend/src/components/ErrorBoundary.tsx`, `frontend/src/components/ToastProvider.tsx`, `frontend/src/hooks/useToast.ts`
**Do**: React error boundary for render crashes. Toast notification system for async errors (upload failed, export failed, etc.). Consistent error display.
**Acceptance**: Render errors show fallback UI, not white screen. API errors show user-friendly toasts. No silent failures.

### T4.2 — Loading states and skeleton screens
**Files**: `frontend/src/components/Skeleton.tsx`, various page/component files
**Do**: Add loading skeletons for: project list, transcript, waveform. Loading spinners for: upload, transcription, export. Disable buttons during pending operations.
**Acceptance**: Every async operation has a visible loading state. No layout shift when data loads.

### T4.3 — Backend structured logging
**Files**: `backend/app/middleware/logging.py`, `backend/app/main.py` (extend)
**Do**: Configure `structlog` with JSON output. Add request_id to all log entries. Log all API requests (method, path, status, duration). Log all worker job transitions.
**Acceptance**: All API requests are logged with correlation IDs. Worker jobs log state transitions. Logs are structured JSON.

### T4.4 — Backend error handling and validation
**Files**: `backend/app/exceptions.py`, `backend/app/middleware/error_handler.py`
**Do**: Define domain exception hierarchy. Global exception handler middleware that catches domain exceptions and returns proper HTTP responses. Validate all request bodies with Pydantic.
**Acceptance**: Invalid requests return 400 with descriptive errors. Domain errors (not found, forbidden, conflict) return correct status codes. No unhandled 500 errors in normal operation.

### T4.5 — Onboarding flow
**Files**: `frontend/src/components/OnboardingWizard.tsx`
**Do**: First-time user flow: create project → name speakers → upload audio per speaker → voice consent → auto-start transcription. Step-by-step wizard with progress indicator.
**Acceptance**: New user can go from signup to viewing their transcript in a guided flow. Each step validates before proceeding.
**Depends on**: T2.6, T2.8

### T4.6 — Audio streaming endpoint
**Files**: `backend/app/api/upload.py` (extend)
**Do**: Range-request-aware audio streaming from Supabase Storage. Enables seeking in the browser without downloading entire files.
**Acceptance**: Audio files can be seeked in the browser. Partial content (206) responses work correctly. Large files don't require full download.

### T4.7 — Rate limiting and file size enforcement
**Files**: `backend/app/middleware/rate_limit.py`, `backend/app/api/upload.py` (extend)
**Do**: Rate limit API endpoints (e.g., 100 req/min per user). Enforce file size limits (500MB per file, 2GB per project). Reject oversized uploads early.
**Acceptance**: Excessive requests return 429. Oversized uploads return 413. Limits are configurable via env vars.

### T4.8 — Frontend production build and deployment config
**Files**: `frontend/vite.config.ts` (extend), `frontend/vercel.json`
**Do**: Optimize production build (code splitting, asset hashing). Configure Vercel deployment with env vars. SPA fallback routing.
**Acceptance**: `npm run build` produces optimized output. Deploy to Vercel succeeds. All routes work in production.

### T4.9 — Backend deployment config
**Files**: `backend/Dockerfile`, `backend/railway.toml`
**Do**: Dockerfile for FastAPI + Celery worker. Railway deployment config. Health check endpoint for Railway. Environment variable configuration.
**Acceptance**: Backend deploys to Railway. Health check passes. Workers process jobs. Environment variables are loaded correctly.

### T4.10 — End-to-end test suite
**Files**: `frontend/e2e/upload-to-export.spec.ts`
**Do**: Playwright test covering the critical path: login → create project → add speakers → upload audio → transcribe → edit transcript → export → download. Uses test fixtures with short audio clips.
**Acceptance**: E2E test passes in CI. Covers the full happy path. Runs in under 2 minutes.
**Depends on**: All Phase 3 tasks

---

## Dependency Graph Summary

```
Phase 1 (Foundation):
T1.1 ─────────────────────────┐
T1.2 ───────────────┐         │
T1.3 ──┬── T1.4     │         │
       ├── T1.5     │         │
       │            │    T1.6 ─┼── T1.7
       │            │         └── T1.8
       │            │
Phase 2 (Core):     │
T1.4+T1.5 → T2.1 → T2.2
T2.1 → T2.3 → T2.4 → T2.5 → T2.6
T2.5 → T2.7 → T2.8 → T2.9 → T2.10
T1.7+T1.8 → T2.2

Phase 3 (Features):
T2.9 → T3.1 → T3.2 → T3.3, T3.4, T3.5, T3.6
T2.5 → T3.7 → T3.8, T3.11
T2.10+T3.2 → T3.9 → T3.10
T3.7+T3.11 → T3.12 → T3.13

Phase 4 (Polish):
T4.1–T4.4: Independent (can start anytime)
T4.5: After T2.6+T2.8
T4.6–T4.7: After T2.5
T4.8–T4.9: After Phase 3
T4.10: After all Phase 3
```

## Clarifications Resolved

1. **Frontend framework**: Vite + React 19 SPA (not Next.js). Audio-heavy client logic doesn't benefit from SSR.
2. **Auth provider**: Supabase Auth (managed, pairs with Supabase DB/Storage, reduces solo-dev burden).
3. **AI provider**: OpenAI APIs for all AI operations (Whisper for transcription, TTS for voice generation/smoothing). Abstracted behind service interfaces for future provider swap.
4. **V1 file limit**: 60 minutes per recording, 500MB per file, 2GB per project.
5. **Collaboration**: NOT in V1. Single-user editing only. V2 adds Yjs/CRDT-based real-time collaboration.
6. **Speaker diarization**: NOT in V1. V1 supports separate file uploads only. V2 adds merged file upload with auto speaker separation.
7. **Job communication**: Polling in V1 (not WebSockets). Acceptable for 10s–5min async jobs.
