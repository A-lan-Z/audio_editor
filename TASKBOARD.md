# TASKBOARD.md

## 1. Purpose

This document tracks all tasks for the TextAudio Edit MVP implementation. AI agents should use this to:
- Track task status and progress
- Understand dependencies before starting work
- Record completion and testing status
- Document blockers and notes

**How to use:**
1. Find the next "Not Started" task with all dependencies satisfied
2. Update status to "In Progress" and add your agent ID to "Agent"
3. Complete the task following acceptance criteria
4. Run tests and update status to "Testing"
5. When all criteria met, update status to "Done" and add completion date
6. Move to next task

---

## 2. Task Status Legend

- **Not Started:** Task ready to begin (check dependencies first)
- **In Progress:** Currently being worked on by an agent
- **Blocked:** Cannot proceed due to dependency or issue (see Notes)
- **Testing:** Implementation complete, undergoing testing/review
- **Done:** All acceptance criteria met, tests passing, committed

---

## 3. Overall Progress

**Phase Summary:**

| Phase | Total Tasks | Not Started | In Progress | Blocked | Testing | Done |
|-------|-------------|-------------|-------------|---------|---------|------|
| 0: Scaffolding | 8 | 8 | 0 | 0 | 0 | 0 |
| 1: Backend Core | 9 | 9 | 0 | 0 | 0 | 0 |
| 2: Audio Input | 10 | 10 | 0 | 0 | 0 | 0 |
| 3: Transcription | 13 | 13 | 0 | 0 | 0 | 0 |
| 4: Text Editor | 12 | 12 | 0 | 0 | 0 | 0 |
| 5: Audio Deletion | 11 | 11 | 0 | 0 | 0 | 0 |
| 6: Voice/TTS | 17 | 17 | 0 | 0 | 0 | 0 |
| 7: Pause Adjust | 10 | 10 | 0 | 0 | 0 | 0 |
| 8: Playback | 11 | 11 | 0 | 0 | 0 | 0 |
| 9: Export | 13 | 13 | 0 | 0 | 0 | 0 |
| 10: Polish | 15 | 15 | 0 | 0 | 0 | 0 |
| **TOTAL** | **119** | **119** | **0** | **0** | **0** | **0** |

**Last Updated:** 2025-12-15
**Current Phase:** 0 (Not Started)
**Next Task:** T001

---

## 4. Task Details by Phase

### Phase 0: Project Scaffolding & Setup

#### T001: Create Directory Structure
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** None
- **Agent:** (unassigned)
- **Requirements:** NFR-4

**Description:**
Create the foundational directory structure for the project:
```
audio_editor/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── models/
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── public/
│   └── index.html
├── tests/
│   ├── backend/
│   └── frontend/
├── scripts/
├── docs/
├── samples/
├── .github/
└── [existing: requirements.md, AI.md, AGENTS.md, WORKPLAN.md, TASKBOARD.md]
```

**Acceptance Criteria:**
- [ ] All directories exist
- [ ] Directory structure documented in README.md
- [ ] .gitkeep files added to empty directories for git tracking

**Notes:**
- Use `mkdir -p` to create nested directories
- Add README.md stubs in major directories explaining their purpose

**Completed:** (date)

---

#### T002: Set Up Python Backend Environment
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** T001
- **Agent:** (unassigned)
- **Requirements:** NFR-4

**Description:**
Initialize Python virtual environment and create requirements.txt with initial dependencies.

**Acceptance Criteria:**
- [ ] Python 3.10+ virtual environment created in `.venv/`
- [ ] requirements.txt includes: fastapi, uvicorn, pydantic, python-multipart, pydub, librosa, soundfile
- [ ] requirements-dev.txt includes: pytest, pytest-cov, black, ruff, mypy
- [ ] Virtual environment can be activated and packages installed
- [ ] .venv/ added to .gitignore

**Notes:**
- Use `python -m venv .venv` for environment creation
- Pin major versions to avoid breaking changes
- Document activation command in README.md

**Completed:** (date)

---

#### T003: Initialize Frontend with Vite + React + TypeScript
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** T001
- **Agent:** (unassigned)
- **Requirements:** NFR-4

**Description:**
Set up frontend project using Vite scaffolding with React and TypeScript.

**Acceptance Criteria:**
- [ ] Frontend initialized with `npm create vite@latest frontend -- --template react-ts`
- [ ] package.json includes: react, react-dom, typescript, vite
- [ ] Dev dependencies include: eslint, prettier, @typescript-eslint/*
- [ ] `npm install` completes successfully
- [ ] `npm run dev` starts development server
- [ ] node_modules/ added to .gitignore

**Notes:**
- Configure Vite to proxy API requests to backend (localhost:8000)
- Set up path aliases (@/ for src/) in tsconfig.json

**Completed:** (date)

---

#### T004: Create .gitignore
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** T002, T003
- **Agent:** (unassigned)
- **Requirements:** NFR-6

**Description:**
Create comprehensive .gitignore to exclude generated files, dependencies, and sensitive data.

**Acceptance Criteria:**
- [ ] .gitignore includes: .venv/, venv/, __pycache__/, *.pyc, node_modules/, dist/, build/
- [ ] Audio files excluded: *.wav, *.mp3, *.ogg, *.flac
- [ ] Model weights excluded: *.pt, *.pth, *.ckpt, models/
- [ ] IDE files excluded: .vscode/, .idea/, *.swp
- [ ] Project data excluded: data/, projects/, exports/
- [ ] OS files excluded: .DS_Store, Thumbs.db

**Notes:**
- Keep samples/ directory tracked but exclude large files
- Document what is gitignored in README.md

**Completed:** (date)

---

#### T005: Set Up Code Formatting Tools
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** T002, T003
- **Agent:** (unassigned)
- **Requirements:** AGENTS.md conventions

**Description:**
Configure black, ruff, prettier, and eslint with project standards.

**Acceptance Criteria:**
- [ ] pyproject.toml created with black config (line-length=88, Python 3.10+)
- [ ] ruff.toml created with linting rules enabled
- [ ] .prettierrc created (semi: false, singleQuote: true, trailingComma: es5)
- [ ] .eslintrc.json created with TypeScript rules
- [ ] All configs tested and working
- [ ] Config files documented in AGENTS.md

**Notes:**
- Follow AGENTS.md guidelines: 4-space indent for Python, 2-space for TS
- Configure ruff to check type hints

**Completed:** (date)

---

#### T006: Create Makefile with Common Commands
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** T002, T003, T005
- **Agent:** (unassigned)
- **Requirements:** AGENTS.md conventions

**Description:**
Create Makefile to standardize common development tasks.

**Acceptance Criteria:**
- [ ] Makefile includes targets: fmt, lint, test, dev, clean, install
- [ ] `make fmt` runs black + ruff format + prettier
- [ ] `make lint` runs ruff check + eslint
- [ ] `make test` runs pytest + vitest (when available)
- [ ] `make dev` launches both backend and frontend concurrently
- [ ] `make install` sets up both backend and frontend dependencies
- [ ] All targets tested and working

**Notes:**
- Use `&&` for sequential commands, `&` for parallel
- Add help target with descriptions: `make help`

**Completed:** (date)

---

#### T007: Write Initial README.md
- **Status:** Not Started
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** T001-T006
- **Agent:** (unassigned)
- **Requirements:** General documentation

**Description:**
Create README.md with project overview, setup instructions, and usage guide.

**Acceptance Criteria:**
- [ ] README.md includes: project name, description, MVP scope
- [ ] Prerequisites section (Python 3.10+, Node 18+, OS requirements)
- [ ] Installation instructions (backend + frontend setup)
- [ ] Running the app (`make dev` or manual commands)
- [ ] Project structure overview
- [ ] Links to requirements.md, AI.md, AGENTS.md, WORKPLAN.md
- [ ] Troubleshooting section (placeholder)

**Notes:**
- Keep it concise for MVP, expand in Phase 10
- Use code blocks for commands

**Completed:** (date)

---

#### T008: Initialize TASKBOARD.md
- **Status:** In Progress
- **Phase:** 0
- **Complexity:** Low
- **Dependencies:** None
- **Agent:** Current AI Agent
- **Requirements:** Project management

**Description:**
Create this TASKBOARD.md file with all tasks from WORKPLAN.md.

**Acceptance Criteria:**
- [ ] All 119 tasks documented with metadata
- [ ] Progress tracking table complete
- [ ] Status legend and usage instructions included
- [ ] Linked to WORKPLAN.md

**Notes:**
- This task is being completed as part of initial workplan creation

**Completed:** 2025-12-15

---

### Phase 1: Backend Core Infrastructure

#### T101: Create FastAPI Application Skeleton
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Low
- **Dependencies:** T002, T006
- **Agent:** (unassigned)
- **Requirements:** NFR-4

**Description:**
Create main FastAPI app with CORS, basic routing, and health check endpoint.

**Acceptance Criteria:**
- [ ] backend/main.py created with FastAPI app instance
- [ ] CORS middleware configured for local frontend origin
- [ ] Health check endpoint: GET /health returns {"status": "ok"}
- [ ] Server starts with `uvicorn backend.main:app --reload`
- [ ] Can access http://localhost:8000/health successfully

**Notes:**
- Use port 8000 for backend (configurable via env var)
- Enable CORS for localhost:5173 (Vite default)

**Completed:** (date)

---

#### T102: Implement Project Data Model
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Medium
- **Dependencies:** T101
- **Agent:** (unassigned)
- **Requirements:** FR-1, FR-2

**Description:**
Create Pydantic models for Project, Transcript, Token, EditOperation.

**Acceptance Criteria:**
- [ ] backend/models/project.py created
- [ ] Project model includes: id (UUID), created_at, updated_at, audio_path, metadata
- [ ] Token model includes: id, text, start, end, type (word/punctuation/pause)
- [ ] Transcript model includes: tokens (list), language, duration
- [ ] EditOperation model includes: type, position, old_tokens, new_text, timestamp
- [ ] All models have proper type hints and validation
- [ ] Models can serialize to/from JSON

**Notes:**
- Use UUID4 for project IDs
- Use datetime for timestamps (ISO 8601 format)
- Token times in seconds (float)

**Completed:** (date)

---

#### T103: Create ProjectManager Service
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Medium
- **Dependencies:** T102
- **Agent:** (unassigned)
- **Requirements:** FR-1, FR-2

**Description:**
Implement service class for project CRUD operations.

**Acceptance Criteria:**
- [ ] backend/services/project_manager.py created
- [ ] ProjectManager class with methods: create_project, get_project, update_project, delete_project
- [ ] In-memory storage for MVP (dict of project_id -> Project)
- [ ] Thread-safe access (use locks if needed)
- [ ] Raises appropriate exceptions for not found, validation errors

**Notes:**
- File-based persistence can be added later (T104)
- Keep interface simple and testable

**Completed:** (date)

---

#### T104: Implement File Storage Utilities
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Medium
- **Dependencies:** T103
- **Agent:** (unassigned)
- **Requirements:** FR-2, NFR-6

**Description:**
Create utilities for saving/loading audio files and project metadata.

**Acceptance Criteria:**
- [ ] backend/utils/storage.py created
- [ ] Functions: save_audio_file, load_audio_file, save_project_metadata, load_project_metadata
- [ ] Project directory structure: projects/{project_id}/
- [ ] Each project folder contains: original.wav, metadata.json, transcript.json, voice_profile/
- [ ] Safe file operations (atomic writes, validation)
- [ ] Handle file not found, permission errors gracefully

**Notes:**
- Store projects in `./data/projects/` by default
- Use json.dump/load for metadata
- Validate file paths to prevent directory traversal

**Completed:** (date)

---

#### T105: Create REST Endpoints for Projects
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Medium
- **Dependencies:** T103, T104
- **Agent:** (unassigned)
- **Requirements:** FR-1, FR-2

**Description:**
Implement API endpoints for project creation and retrieval.

**Acceptance Criteria:**
- [ ] POST /api/projects creates new project, returns project_id and metadata
- [ ] GET /api/projects/{id} retrieves project metadata
- [ ] GET /api/projects lists all projects (optional for MVP)
- [ ] Endpoints use Pydantic request/response models
- [ ] Proper HTTP status codes (201, 200, 404, 400)
- [ ] Can test endpoints with curl or Postman

**Notes:**
- Keep response format consistent across endpoints
- Use FastAPI dependency injection for ProjectManager

**Completed:** (date)

---

#### T106: Add Request/Response Validation
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Low
- **Dependencies:** T105
- **Agent:** (unassigned)
- **Requirements:** NFR-10

**Description:**
Add comprehensive validation for all API inputs and outputs.

**Acceptance Criteria:**
- [ ] All endpoints use Pydantic models for validation
- [ ] Invalid requests return 422 with clear error messages
- [ ] Request body size limits configured (e.g., 100MB for audio)
- [ ] UUID validation for project_id parameters
- [ ] Test invalid inputs return proper errors

**Notes:**
- Use FastAPI's built-in validation
- Customize error messages for clarity

**Completed:** (date)

---

#### T107: Implement Error Handling Middleware
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Medium
- **Dependencies:** T105
- **Agent:** (unassigned)
- **Requirements:** NFR-10

**Description:**
Create global exception handlers for consistent error responses.

**Acceptance Criteria:**
- [ ] Custom exception classes: ProjectNotFound, InvalidAudioFormat, etc.
- [ ] Exception handler middleware catches all errors
- [ ] Error response format: {error: str, detail: str, code: str}
- [ ] 404 for not found, 400 for validation, 500 for server errors
- [ ] Stack traces hidden in production (but logged)
- [ ] User-friendly error messages (NFR-10)

**Notes:**
- Don't expose internal paths or sensitive info in errors
- Log full errors server-side for debugging

**Completed:** (date)

---

#### T108: Add Basic Logging Configuration
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Low
- **Dependencies:** T101
- **Agent:** (unassigned)
- **Requirements:** NFR-8

**Description:**
Configure Python logging with appropriate levels and format.

**Acceptance Criteria:**
- [ ] backend/utils/logging_config.py created
- [ ] Logging configured: INFO level, file + console output
- [ ] Log format includes: timestamp, level, module, message
- [ ] Logs written to ./logs/app.log
- [ ] NO audio content or transcripts logged (NFR-8)
- [ ] Log rotation configured (e.g., 10MB max, 5 files)

**Notes:**
- Use Python's logging.config
- Sanitize any logged data (remove PII)

**Completed:** (date)

---

#### T109: Write Unit Tests for Core Services
- **Status:** Not Started
- **Phase:** 1
- **Complexity:** Medium
- **Dependencies:** T103, T104, T107
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Create pytest tests for ProjectManager and storage utilities.

**Acceptance Criteria:**
- [ ] tests/backend/test_project_manager.py created
- [ ] tests/backend/test_storage.py created
- [ ] Test coverage >80% for both modules
- [ ] Tests for: create, retrieve, update, not found scenarios
- [ ] Tests for file save/load with edge cases
- [ ] All tests passing with `pytest`

**Notes:**
- Use pytest fixtures for test data
- Mock file system operations where appropriate
- Use tmp_path fixture for file tests

**Completed:** (date)

---

### Phase 2: Audio Input & Validation

#### T201: Implement Audio Upload Endpoint
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T105
- **Agent:** (unassigned)
- **Requirements:** FR-3

**Description:**
Create endpoint to receive audio file uploads.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/upload endpoint implemented
- [ ] Accepts multipart/form-data with audio file
- [ ] Saves uploaded file to project directory
- [ ] Returns upload status and file metadata
- [ ] Handles large files (up to 100MB)
- [ ] Can upload via curl or Postman successfully

**Notes:**
- Use FastAPI's UploadFile
- Validate content-type before processing
- Store as original filename initially, rename after validation

**Completed:** (date)

---

#### T202: Add Audio Format Validation and Conversion
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T201
- **Agent:** (unassigned)
- **Requirements:** FR-3

**Description:**
Validate audio format and convert to standard format if needed.

**Acceptance Criteria:**
- [ ] backend/utils/audio_processing.py created
- [ ] Validates file extensions: .wav, .mp3
- [ ] Validates actual audio format using librosa/soundfile
- [ ] Converts to WAV (16-bit PCM) if needed using pydub
- [ ] Rejects unsupported formats with clear error
- [ ] Test with various audio files (WAV, MP3, invalid formats)

**Notes:**
- Use pydub for format detection and conversion
- Handle corrupt files gracefully

**Completed:** (date)

---

#### T203: Implement Duration Check
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Low
- **Dependencies:** T202
- **Agent:** (unassigned)
- **Requirements:** FR-4

**Description:**
Check audio duration and reject files exceeding limit.

**Acceptance Criteria:**
- [ ] Function to get audio duration using librosa
- [ ] Hard limit: 10 minutes (600 seconds)
- [ ] Reject longer files with error: "This file is too long (X min). Max 10 minutes."
- [ ] Log warning for files >5 minutes
- [ ] Test with audio files of various lengths

**Notes:**
- Use librosa.get_duration() for accuracy
- Duration check happens after format validation

**Completed:** (date)

---

#### T204: Normalize Audio to Mono and Standard Sample Rate
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T202
- **Agent:** (unassigned)
- **Requirements:** FR-5

**Description:**
Convert audio to mono and consistent sample rate for model compatibility.

**Acceptance Criteria:**
- [ ] Converts stereo to mono (mix channels)
- [ ] Resamples to 16kHz (or 24kHz if preferred by ASR model)
- [ ] Saves normalized audio as projects/{id}/original.wav
- [ ] Preserves audio quality during conversion
- [ ] Test with mono, stereo, various sample rates

**Notes:**
- Use librosa.resample and librosa.to_mono
- Document chosen sample rate in comments

**Completed:** (date)

---

#### T205: Store Original Audio in Project Directory
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Low
- **Dependencies:** T204
- **Agent:** (unassigned)
- **Requirements:** FR-2, NFR-6

**Description:**
Save processed audio to project-specific directory structure.

**Acceptance Criteria:**
- [ ] Audio saved to data/projects/{project_id}/original.wav
- [ ] Metadata updated with audio_path, duration, sample_rate, channels
- [ ] Original uploaded file discarded after processing
- [ ] Verify file exists and is readable after save
- [ ] Project metadata persisted to disk

**Notes:**
- Use atomic file writes (write to temp, then rename)
- Update Project model with audio metadata

**Completed:** (date)

---

#### T206: Create Frontend File Upload Component
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T003, T201
- **Agent:** (unassigned)
- **Requirements:** FR-3, NFR-9

**Description:**
Build React component for audio file upload with drag-and-drop.

**Acceptance Criteria:**
- [ ] frontend/src/components/AudioUpload.tsx created
- [ ] Drag-and-drop zone for audio files
- [ ] Click to browse file picker
- [ ] Shows selected file name and size
- [ ] Upload button triggers POST to /api/projects/{id}/upload
- [ ] Validates file type client-side (.wav, .mp3)
- [ ] Component tested in browser

**Notes:**
- Use HTML5 drag-and-drop API
- Show clear visual feedback (hover state, file selected)

**Completed:** (date)

---

#### T207: Implement Browser-Based Audio Recording
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T003
- **Agent:** (unassigned)
- **Requirements:** FR-5

**Description:**
Add audio recording capability using MediaRecorder API.

**Acceptance Criteria:**
- [ ] frontend/src/components/AudioRecorder.tsx created
- [ ] Requests microphone permission on mount
- [ ] Start/Stop recording buttons
- [ ] Records as WebM or WAV (browser-dependent)
- [ ] Returns Blob when recording stops
- [ ] Handles permission denied gracefully
- [ ] Test in Chrome and Firefox

**Notes:**
- Use MediaRecorder with audio-only constraints
- Default to mono recording if supported
- Handle browser compatibility issues

**Completed:** (date)

---

#### T208: Add Recording UI with Playback Preview
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T207
- **Agent:** (unassigned)
- **Requirements:** FR-5, NFR-9

**Description:**
Create UI for recording with visual feedback and preview.

**Acceptance Criteria:**
- [ ] Shows recording indicator (red dot, timer)
- [ ] Displays duration while recording
- [ ] Stop button ends recording
- [ ] Preview playback of recorded audio before upload
- [ ] Re-record button to try again
- [ ] Confirm and upload button sends to backend
- [ ] Clear, intuitive layout (NFR-9)

**Notes:**
- Use HTML5 audio element for preview
- Show waveform visualization (optional, nice-to-have)

**Completed:** (date)

---

#### T209: Display Upload Progress and Errors
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Low
- **Dependencies:** T206, T208
- **Agent:** (unassigned)
- **Requirements:** NFR-9, NFR-10

**Description:**
Show upload progress bar and handle errors gracefully in UI.

**Acceptance Criteria:**
- [ ] Progress bar shows upload percentage
- [ ] Shows processing status after upload (validating, converting)
- [ ] Displays success message when complete
- [ ] Shows user-friendly error messages (file too large, unsupported format, etc.)
- [ ] Error messages match backend responses
- [ ] Can retry after error

**Notes:**
- Use XMLHttpRequest or fetch with progress events
- Style errors in red, success in green

**Completed:** (date)

---

#### T210: Write Integration Tests for Upload
- **Status:** Not Started
- **Phase:** 2
- **Complexity:** Medium
- **Dependencies:** T201-T205
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Create tests for complete upload workflow.

**Acceptance Criteria:**
- [ ] tests/backend/test_upload.py created
- [ ] Test valid WAV upload
- [ ] Test valid MP3 upload and conversion
- [ ] Test file too long (>10 min) rejection
- [ ] Test invalid format rejection
- [ ] Test corrupt file handling
- [ ] All tests passing

**Notes:**
- Use pytest-httpx for API testing
- Create sample audio fixtures (librosa can generate)

**Completed:** (date)

---

### Phase 3: Automatic Speech Recognition (Transcription)

#### T301: Research and Select ASR Model
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Low
- **Dependencies:** T002
- **Agent:** (unassigned)
- **Requirements:** FR-6, FR-7, NFR-1

**Description:**
Research ASR options and select model for MVP.

**Acceptance Criteria:**
- [ ] Researched options: Whisper, faster-whisper, Vosk, alternatives
- [ ] Selected model documented with rationale
- [ ] Verified model can run locally
- [ ] Verified model provides word-level timestamps
- [ ] Performance estimate documented (time per minute of audio)
- [ ] Decision documented in docs/architecture.md

**Notes:**
- Recommend: faster-whisper (good speed/accuracy balance)
- Check GPU vs CPU performance
- Consider model size (base, small, medium, large)

**Completed:** (date)

---

#### T302: Create TranscriptionService Interface
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Low
- **Dependencies:** T301
- **Agent:** (unassigned)
- **Requirements:** AI.md (interfaces)

**Description:**
Define abstract interface for transcription services.

**Acceptance Criteria:**
- [ ] backend/services/transcription_service.py created
- [ ] Abstract class TranscriptionService with methods:
  - transcribe(audio_path: str) -> Transcript
  - get_word_timestamps(audio_path: str) -> List[Token]
- [ ] Allows swapping implementations
- [ ] Type hints and docstrings complete

**Notes:**
- Enables testing with mock service
- Future: support multiple ASR backends

**Completed:** (date)

---

#### T303: Implement WhisperTranscriptionService
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** High
- **Dependencies:** T302
- **Agent:** (unassigned)
- **Requirements:** FR-6, FR-7, FR-8

**Description:**
Implement concrete Whisper-based transcription service.

**Acceptance Criteria:**
- [ ] backend/services/whisper_service.py created
- [ ] Implements TranscriptionService interface
- [ ] Uses faster-whisper or openai-whisper library
- [ ] Extracts word-level timestamps from output
- [ ] Handles audio file loading and preprocessing
- [ ] Returns Transcript with Token list
- [ ] Test with sample audio file

**Notes:**
- Use faster-whisper for better performance
- Model size: start with "base" or "small" for MVP
- Language: "en" for English

**Completed:** (date)

---

#### T304: Add Model Download/Initialization
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T303
- **Agent:** (unassigned)
- **Requirements:** NFR-4, NFR-5

**Description:**
Handle automatic model download and initialization on first run.

**Acceptance Criteria:**
- [ ] Model downloads automatically on first transcription
- [ ] Models stored in ./models/ directory (gitignored)
- [ ] Download progress shown in logs
- [ ] Models cached for subsequent use
- [ ] Handles download failures gracefully
- [ ] Model path configurable via environment variable

**Notes:**
- Use HuggingFace model hub or Whisper's built-in downloader
- Document model size requirements in README

**Completed:** (date)

---

#### T305: Implement Word-Level Timestamp Extraction
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T303
- **Agent:** (unassigned)
- **Requirements:** FR-7

**Description:**
Extract precise word-level timestamps from ASR output.

**Acceptance Criteria:**
- [ ] Each word has start_time and end_time in seconds
- [ ] Timestamp precision <100ms
- [ ] Handles punctuation (attach to previous word or separate token)
- [ ] Validates timestamps (no overlaps, monotonically increasing)
- [ ] Test timestamp accuracy with known audio

**Notes:**
- Whisper provides word timestamps with word_timestamps=True
- Validate: end_time > start_time, next.start >= prev.end

**Completed:** (date)

---

#### T306: Create Transcript Data Model
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Low
- **Dependencies:** T102, T305
- **Agent:** (unassigned)
- **Requirements:** FR-7, FR-9

**Description:**
Define Transcript and Token models for structured data.

**Acceptance Criteria:**
- [ ] backend/models/transcript.py created
- [ ] Token model: id (UUID), text (str), start (float), end (float), type (enum: word/punctuation/pause)
- [ ] Transcript model: tokens (List[Token]), language (str), duration (float), created_at (datetime)
- [ ] Methods: to_json(), from_json(), to_text()
- [ ] Validation: timestamps valid, non-empty text

**Notes:**
- Use Pydantic for validation
- to_text() reconstructs plain text from tokens

**Completed:** (date)

---

#### T307: Add Transcription Endpoint
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T303, T306
- **Agent:** (unassigned)
- **Requirements:** FR-6, FR-7

**Description:**
Create API endpoint to trigger transcription.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/transcribe endpoint
- [ ] Validates audio file exists
- [ ] Calls TranscriptionService.transcribe()
- [ ] Saves transcript to projects/{id}/transcript.json
- [ ] Updates project metadata with transcript_path
- [ ] Returns transcript JSON
- [ ] Test with curl/Postman

**Notes:**
- Transcription is synchronous for now (T308 adds async)
- May take 1-2 minutes for 5min audio

**Completed:** (date)

---

#### T308: Handle Transcription Progress/Status Polling
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** High
- **Dependencies:** T307
- **Agent:** (unassigned)
- **Requirements:** NFR-1

**Description:**
Make transcription async with progress tracking.

**Acceptance Criteria:**
- [ ] Transcription runs in background thread/task
- [ ] Returns task_id immediately (202 Accepted)
- [ ] GET /api/projects/{id}/transcribe/status returns progress
- [ ] Status: queued, processing, completed, failed
- [ ] Optional: progress percentage (estimated)
- [ ] Frontend can poll for completion
- [ ] Completed transcription available via GET /api/projects/{id}/transcript

**Notes:**
- Use asyncio or threading
- Store task state in memory (or Redis for production)
- Consider WebSocket for real-time updates (optional)

**Completed:** (date)

---

#### T309: Store Transcript JSON
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Low
- **Dependencies:** T306, T307
- **Agent:** (unassigned)
- **Requirements:** FR-2

**Description:**
Persist transcript to project directory in JSON format.

**Acceptance Criteria:**
- [ ] Transcript saved to projects/{id}/transcript.json
- [ ] JSON format: {"tokens": [...], "language": "en", "duration": 300.5, ...}
- [ ] File is human-readable (pretty-printed)
- [ ] Can be loaded back into Transcript model
- [ ] Test save/load roundtrip

**Notes:**
- Use Pydantic's .json() method
- Include indent=2 for readability

**Completed:** (date)

---

#### T310: Create Frontend Transcription Trigger Component
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T003, T307
- **Agent:** (unassigned)
- **Requirements:** FR-9, NFR-9

**Description:**
Build UI to trigger transcription after upload.

**Acceptance Criteria:**
- [ ] frontend/src/components/TranscriptionTrigger.tsx created
- [ ] "Generate Transcript" button
- [ ] Button disabled if no audio uploaded
- [ ] Triggers POST /api/projects/{id}/transcribe
- [ ] Shows loading state while processing
- [ ] Displays success when transcript ready
- [ ] Handles errors (file not found, etc.)

**Notes:**
- Integrate with upload workflow (auto-advance to transcription)
- Clear visual feedback (spinner, progress message)

**Completed:** (date)

---

#### T311: Display Transcription Status
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T308, T310
- **Agent:** (unassigned)
- **Requirements:** NFR-9

**Description:**
Show real-time transcription progress in UI.

**Acceptance Criteria:**
- [ ] Polls GET /api/projects/{id}/transcribe/status every 2 seconds
- [ ] Shows status: "Queued", "Processing...", "Completed", "Failed"
- [ ] Optional: shows progress bar or percentage
- [ ] Stops polling when completed or failed
- [ ] Fetches transcript when completed
- [ ] Shows error message if failed

**Notes:**
- Use setInterval for polling
- Clear interval on unmount to prevent leaks
- Consider adding estimated time remaining

**Completed:** (date)

---

#### T312: Write Tests with Sample Audio
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T303, T307
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Create comprehensive tests for transcription pipeline.

**Acceptance Criteria:**
- [ ] tests/backend/test_transcription.py created
- [ ] Sample audio files created (2-5 min synthetic speech)
- [ ] Test: transcribe sample, verify tokens returned
- [ ] Test: timestamp accuracy (known words at known times)
- [ ] Test: handles empty audio
- [ ] Test: handles corrupt audio file
- [ ] All tests passing

**Notes:**
- Use librosa or pydub to generate synthetic audio
- Mock ASR model for unit tests, use real model for integration tests

**Completed:** (date)

---

#### T313: Measure and Optimize Transcription Performance
- **Status:** Not Started
- **Phase:** 3
- **Complexity:** Medium
- **Dependencies:** T312
- **Agent:** (unassigned)
- **Requirements:** NFR-1

**Description:**
Profile transcription and optimize to meet performance targets.

**Acceptance Criteria:**
- [ ] Benchmark: 5-minute audio transcribed in <2 minutes
- [ ] Profile with cProfile or similar tool
- [ ] Identify bottlenecks (model loading, inference, I/O)
- [ ] Optimize: use faster-whisper, reduce model size, or GPU if available
- [ ] Document performance characteristics (CPU vs GPU, model size trade-offs)
- [ ] Performance notes added to docs/

**Notes:**
- NFR-1 target: ~1-2 min for 5 min audio
- Consider batch processing if needed
- Document hardware requirements

**Completed:** (date)

---

### Phase 4: Text Editor & Token Mapping

#### T401: Design Token-to-Audio Mapping Data Structure
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** Medium
- **Dependencies:** T306
- **Agent:** (unassigned)
- **Requirements:** FR-10, FR-11

**Description:**
Design data structure to maintain text-to-audio alignment.

**Acceptance Criteria:**
- [ ] Design documented in docs/architecture.md
- [ ] Structure maps: character positions in text ↔ token IDs ↔ audio timestamps
- [ ] Handles insertions, deletions, and replacements
- [ ] Preserves original token metadata even when edited
- [ ] Efficient lookups (O(log n) for position-to-token)
- [ ] Design reviewed and approved

**Notes:**
- Consider using offset-based indexing
- Track original vs. current text positions
- May need auxiliary index structures (interval tree?)

**Completed:** (date)

---

#### T402: Create TranscriptEditor React Component
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** High
- **Dependencies:** T003, T306
- **Agent:** (unassigned)
- **Requirements:** FR-10, FR-13

**Description:**
Build main transcript editor component.

**Acceptance Criteria:**
- [ ] frontend/src/components/TranscriptEditor.tsx created
- [ ] Renders transcript as editable text (contentEditable or textarea)
- [ ] Supports text selection, cursor movement
- [ ] Supports keyboard shortcuts (Ctrl+Z for undo, etc.)
- [ ] Maintains internal state of transcript tokens
- [ ] Emits edit events to parent component
- [ ] Basic styling (readable font, padding)

**Notes:**
- Use contentEditable div for rich control, or controlled textarea
- Consider using Slate.js or similar editor library for advanced features
- Keep simple for MVP, can enhance later

**Completed:** (date)

---

#### T403: Render Transcript from Token List
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** Medium
- **Dependencies:** T402
- **Agent:** (unassigned)
- **Requirements:** FR-9, FR-11

**Description:**
Display transcript by rendering each token as a span.

**Acceptance Criteria:**
- [ ] Each token rendered as <span data-token-id={id}>{text}</span>
- [ ] Tokens concatenated with appropriate spacing
- [ ] Punctuation attached to previous word (no space before)
- [ ] Preserves line breaks and paragraphs (if present)
- [ ] Can reconstruct full text from tokens
- [ ] Visual appearance matches plain text editor

**Notes:**
- Use data attributes to track token IDs
- Handle edge cases: empty tokens, leading/trailing spaces

**Completed:** (date)

---

#### T404: Implement Cursor Position to Token ID Mapping
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** High
- **Dependencies:** T403
- **Agent:** (unassigned)
- **Requirements:** FR-11

**Description:**
Map cursor position in editor to corresponding token.

**Acceptance Criteria:**
- [ ] Function: getTokenAtCursor(cursorPosition) -> Token | null
- [ ] Works with contentEditable cursor position (Selection API)
- [ ] Handles positions between tokens correctly
- [ ] Handles start/end of document
- [ ] Test with various cursor positions
- [ ] Returns null if position is in inserted (non-token) text

**Notes:**
- Use window.getSelection() and Range API
- Walk DOM tree to find token span at cursor

**Completed:** (date)

---

#### T405: Add Text Selection to Token Range Mapping
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** High
- **Dependencies:** T404
- **Agent:** (unassigned)
- **Requirements:** FR-12

**Description:**
Map text selection to range of tokens.

**Acceptance Criteria:**
- [ ] Function: getTokensInSelection() -> Token[]
- [ ] Returns all tokens fully or partially selected
- [ ] Handles multi-line selections
- [ ] Handles partial token selections (include if >50% selected)
- [ ] Test with various selection scenarios
- [ ] Works with keyboard selection (Shift+arrows) and mouse

**Notes:**
- Use Selection API getRangeAt()
- Handle edge case: selection spans non-token text

**Completed:** (date)

---

#### T406: Implement Edit Tracking
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** High
- **Dependencies:** T405
- **Agent:** (unassigned)
- **Requirements:** FR-13

**Description:**
Track all text edits as structured operations.

**Acceptance Criteria:**
- [ ] Capture edits: insertion, deletion, replacement
- [ ] Create EditOperation for each edit: {type, position, old_tokens, new_text, timestamp}
- [ ] Maintain edit history (list of operations)
- [ ] Handle complex edits (cut, paste, drag-and-drop)
- [ ] Debounce rapid edits (e.g., typing) into single operation
- [ ] Test various editing scenarios

**Notes:**
- Listen to input, beforeinput, or keydown events
- Use MutationObserver for contentEditable changes
- Store operations in React state

**Completed:** (date)

---

#### T407: Create EditOperation Data Model
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** Low
- **Dependencies:** T306
- **Agent:** (unassigned)
- **Requirements:** FR-13

**Description:**
Define data model for edit operations.

**Acceptance Criteria:**
- [ ] backend/models/edit_operation.py created
- [ ] EditOperation model: id, type (insert/delete/replace), position, old_tokens (List[UUID]), new_text, timestamp
- [ ] Validation: type is valid, position >= 0
- [ ] Methods: to_json(), from_json(), apply(transcript) -> Transcript
- [ ] Test serialization and application

**Notes:**
- position is character offset in current text
- old_tokens references original token IDs

**Completed:** (date)

---

#### T408: Add Edit Submission Endpoint
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** Medium
- **Dependencies:** T407
- **Agent:** (unassigned)
- **Requirements:** FR-13

**Description:**
Create endpoint to submit edits to backend.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/edit endpoint
- [ ] Request body: EditOperation JSON
- [ ] Validates edit operation
- [ ] Updates project metadata with edit log
- [ ] Returns updated transcript state
- [ ] Test with curl/Postman

**Notes:**
- Edit operations are append-only (for undo support)
- Backend maintains authoritative state

**Completed:** (date)

---

#### T409: Implement Undo/Redo Functionality
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** Medium
- **Dependencies:** T406, T408
- **Agent:** (unassigned)
- **Requirements:** FR-13

**Description:**
Add undo/redo for text edits.

**Acceptance Criteria:**
- [ ] Undo stack maintains last 10+ operations
- [ ] Redo stack populated when undo performed
- [ ] Ctrl+Z (Cmd+Z) triggers undo
- [ ] Ctrl+Shift+Z triggers redo
- [ ] UI buttons for undo/redo (disabled when stack empty)
- [ ] Test undo/redo with various edit sequences
- [ ] Undo/redo syncs with backend

**Notes:**
- Use command pattern for operations
- Clear redo stack on new edit
- Optional: persist undo history to backend

**Completed:** (date)

---

#### T410: Add Visual Highlighting for Edited Regions
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** Medium
- **Dependencies:** T403, T406
- **Agent:** (unassigned)
- **Requirements:** FR-11

**Description:**
Visually distinguish original vs. edited text.

**Acceptance Criteria:**
- [ ] Original tokens: default styling
- [ ] Deleted tokens: strikethrough + gray color
- [ ] Inserted text: green background or underline
- [ ] Replaced tokens: yellow background or highlight
- [ ] Generated audio segments: blue background or badge
- [ ] Styling is clear but not distracting
- [ ] Test various edit combinations

**Notes:**
- Use CSS classes: .token-original, .token-deleted, .token-inserted, .token-replaced
- Update class on edit operations

**Completed:** (date)

---

#### T411: Maintain Token Mapping Integrity After Edits
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** High
- **Dependencies:** T406, T408
- **Agent:** (unassigned)
- **Requirements:** FR-11

**Description:**
Ensure token-to-audio mapping remains correct after edits.

**Acceptance Criteria:**
- [ ] After deletion: removed tokens marked, indices adjusted
- [ ] After insertion: new text has no token mapping (yet)
- [ ] After replacement: old tokens marked, new text tracked separately
- [ ] Timeline remains consistent (no timestamp overlaps)
- [ ] Can reconstruct audio from token mapping
- [ ] Test complex edit sequences (delete, then replace, then undo)

**Notes:**
- May need to re-index tokens after operations
- Preserve original token IDs for reference

**Completed:** (date)

---

#### T412: Write Tests for Edit Operations
- **Status:** Not Started
- **Phase:** 4
- **Complexity:** High
- **Dependencies:** T407, T411
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Comprehensive tests for editing logic.

**Acceptance Criteria:**
- [ ] tests/backend/test_edit_operations.py created
- [ ] Test: delete single word
- [ ] Test: delete multiple words
- [ ] Test: insert text at position
- [ ] Test: replace word
- [ ] Test: undo/redo operations
- [ ] Test: complex sequences
- [ ] Test: token mapping integrity
- [ ] All tests passing

**Notes:**
- Use fixtures for sample transcripts
- Test edge cases: delete all, insert at start/end

**Completed:** (date)

---

### Phase 5: Text-Based Deletion → Audio Editing

#### T501: Create AudioSegmentManager Service
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T306
- **Agent:** (unassigned)
- **Requirements:** FR-14, FR-15

**Description:**
Service to manage audio segments and their states.

**Acceptance Criteria:**
- [ ] backend/services/audio_segment_manager.py created
- [ ] AudioSegment model: id, source (original/generated), file_path, start, end, status (kept/removed)
- [ ] Methods: get_all_segments, mark_removed, mark_kept, add_generated_segment
- [ ] Maintains segment list in timeline order
- [ ] Test segment operations

**Notes:**
- Segments reference token IDs for mapping
- Source "original" means from uploaded audio

**Completed:** (date)

---

#### T502: Implement Segment Marking
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Low
- **Dependencies:** T501
- **Agent:** (unassigned)
- **Requirements:** FR-14

**Description:**
Mark segments as kept/removed/generated.

**Acceptance Criteria:**
- [ ] Segment status enum: kept, removed, generated
- [ ] Function: mark_segment_removed(segment_id)
- [ ] Function: mark_segment_kept(segment_id)
- [ ] Status changes tracked in segment metadata
- [ ] Test status changes and retrieval

**Notes:**
- Don't delete original audio, just mark status
- Allows undo operation

**Completed:** (date)

---

#### T503: Add Deletion Handler
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T407, T502
- **Agent:** (unassigned)
- **Requirements:** FR-14

**Description:**
Map deleted tokens to audio segments and mark as removed.

**Acceptance Criteria:**
- [ ] Function: handle_deletion(edit_operation) -> List[segment_ids]
- [ ] Finds all segments corresponding to deleted token IDs
- [ ] Marks those segments as removed
- [ ] Updates project metadata
- [ ] Returns list of affected segment IDs
- [ ] Test with various deletion scenarios

**Notes:**
- Multiple tokens may map to one segment or vice versa
- Handle partial segment deletions (may need segment splitting)

**Completed:** (date)

---

#### T504: Update Project Metadata for Removed Segments
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Low
- **Dependencies:** T503
- **Agent:** (unassigned)
- **Requirements:** FR-14

**Description:**
Persist segment removal state in project data.

**Acceptance Criteria:**
- [ ] Project metadata includes: segments[] with status
- [ ] Metadata updated when segments marked removed
- [ ] Metadata saved to disk after changes
- [ ] Can load project and restore segment states
- [ ] Test save/load roundtrip

**Notes:**
- Store in projects/{id}/metadata.json
- Include edit operation history

**Completed:** (date)

---

#### T505: Create AudioRenderer Service
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** High
- **Dependencies:** T501
- **Agent:** (unassigned)
- **Requirements:** FR-15, FR-16

**Description:**
Service to assemble audio from segments for playback.

**Acceptance Criteria:**
- [ ] backend/services/audio_renderer.py created
- [ ] Function: render(project_id) -> audio_array
- [ ] Loads all segments with status=kept or status=generated
- [ ] Concatenates in timeline order
- [ ] Returns numpy array or audio file path
- [ ] Test with sample segments

**Notes:**
- Use librosa or soundfile for audio loading
- Output sample rate matches original

**Completed:** (date)

---

#### T506: Implement Segment Concatenation Logic
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T505
- **Agent:** (unassigned)
- **Requirements:** FR-16

**Description:**
Concatenate audio segments seamlessly.

**Acceptance Criteria:**
- [ ] Segments concatenated in correct order
- [ ] No gaps or overlaps in timeline
- [ ] Audio segments aligned to sample boundaries
- [ ] Handles segments from different sources (original + generated)
- [ ] Test concatenation with 3+ segments
- [ ] Output audio is continuous

**Notes:**
- Use np.concatenate for audio arrays
- Ensure sample rate consistency

**Completed:** (date)

---

#### T507: Add Cross-Fade at Segment Boundaries
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T506
- **Agent:** (unassigned)
- **Requirements:** FR-16

**Description:**
Apply short cross-fade to avoid clicks at boundaries.

**Acceptance Criteria:**
- [ ] Cross-fade duration: 10-50ms (configurable)
- [ ] Linear or cosine fade applied at each boundary
- [ ] Fade-out last 10ms of segment A, fade-in first 10ms of segment B, overlap
- [ ] No audible clicks or pops
- [ ] Test with various segment combinations
- [ ] Optional: skip cross-fade for natural boundaries (e.g., pauses)

**Notes:**
- Use librosa or manual array multiplication for fades
- Preserve overall volume level

**Completed:** (date)

---

#### T508: Create Playback Preview Endpoint
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T505, T507
- **Agent:** (unassigned)
- **Requirements:** FR-15

**Description:**
Endpoint to stream assembled audio for preview.

**Acceptance Criteria:**
- [ ] GET /api/projects/{id}/preview endpoint
- [ ] Renders audio with AudioRenderer
- [ ] Returns audio file (WAV) for streaming
- [ ] Generates on-demand (no permanent file yet)
- [ ] Handles large audio efficiently (streaming or chunked)
- [ ] Test with curl or browser

**Notes:**
- Use FastAPI's StreamingResponse
- Consider caching rendered audio temporarily

**Completed:** (date)

---

#### T509: Frontend - Show Deletion Effects in Real-Time
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T410, T503
- **Agent:** (unassigned)
- **Requirements:** FR-14

**Description:**
Update UI to show deleted text visually.

**Acceptance Criteria:**
- [ ] Deleted tokens shown with strikethrough
- [ ] Deleted tokens grayed out
- [ ] Deletion reflected immediately after edit
- [ ] Can toggle visibility of deleted text (optional)
- [ ] Test deletion visual feedback

**Notes:**
- Use CSS for styling (.token-deleted class)
- Maintain deleted tokens in DOM for undo

**Completed:** (date)

---

#### T510: Frontend - Add Preview Edit Button
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Low
- **Dependencies:** T508
- **Agent:** (unassigned)
- **Requirements:** FR-15

**Description:**
Button to preview edited audio before exporting.

**Acceptance Criteria:**
- [ ] "Preview Edited Audio" button in UI
- [ ] Button triggers GET /api/projects/{id}/preview
- [ ] Plays returned audio in browser
- [ ] Shows loading state while rendering
- [ ] Handles errors (e.g., no edits made)
- [ ] Test preview functionality

**Notes:**
- Use HTML5 audio element
- Provide visual feedback (playing indicator)

**Completed:** (date)

---

#### T511: Write Tests for Segment Operations
- **Status:** Not Started
- **Phase:** 5
- **Complexity:** Medium
- **Dependencies:** T501-T507
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Test audio segment management and rendering.

**Acceptance Criteria:**
- [ ] tests/backend/test_audio_segments.py created
- [ ] Test: mark segment as removed
- [ ] Test: concatenate 3 segments
- [ ] Test: cross-fade between segments
- [ ] Test: render with mixed kept/removed segments
- [ ] Test: handle empty segment list
- [ ] All tests passing

**Notes:**
- Use synthetic audio for testing
- Verify output audio properties (duration, sample rate)

**Completed:** (date)

---

### Phase 6: Voice Learning & TTS Replacement

#### T601: Research and Select Voice Cloning TTS Model
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T002
- **Agent:** (unassigned)
- **Requirements:** FR-20, FR-22

**Description:**
Research TTS models with voice cloning capability.

**Acceptance Criteria:**
- [ ] Researched options: Coqui TTS (XTTS), Bark, Tortoise, others
- [ ] Selected model documented with rationale
- [ ] Verified model can clone voice from short sample (<5 min)
- [ ] Verified model runs locally
- [ ] Quality assessment: "good demo quality"
- [ ] Decision documented in docs/architecture.md

**Notes:**
- Coqui XTTS v2 is strong candidate (multi-lingual, fast)
- Check hardware requirements (GPU recommended)
- Evaluate generation speed vs. quality trade-off

**Completed:** (date)

---

#### T602: Create VoiceModelService Interface
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Low
- **Dependencies:** T601
- **Agent:** (unassigned)
- **Requirements:** AI.md (interfaces)

**Description:**
Define abstract interface for voice cloning services.

**Acceptance Criteria:**
- [ ] backend/services/voice_model_service.py created
- [ ] Abstract class VoiceModelService with methods:
  - extract_voice_profile(audio_path: str) -> VoiceProfile
  - generate_speech(text: str, voice_profile: VoiceProfile) -> audio_array
- [ ] Allows swapping TTS implementations
- [ ] Type hints and docstrings complete

**Notes:**
- Enables testing with mock service
- Future: support multiple TTS backends

**Completed:** (date)

---

#### T603: Implement Voice Embedding Extraction
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** High
- **Dependencies:** T602
- **Agent:** (unassigned)
- **Requirements:** FR-20

**Description:**
Extract speaker embedding from reference audio.

**Acceptance Criteria:**
- [ ] Function: extract_voice_profile(audio_path) -> VoiceProfile
- [ ] Uses TTS model's speaker encoder
- [ ] Works with 2-5 minute audio samples
- [ ] Returns embedding/profile (vector or file)
- [ ] Profile can be serialized and saved
- [ ] Test with sample audio

**Notes:**
- XTTS uses speaker encoder to extract embedding
- Embedding is typically a fixed-size vector (192 or 512 dims)

**Completed:** (date)

---

#### T604: Add Automatic Voice Profile Generation
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T603, T307
- **Agent:** (unassigned)
- **Requirements:** FR-20

**Description:**
Automatically generate voice profile after transcription.

**Acceptance Criteria:**
- [ ] Voice profile extracted after transcription completes
- [ ] Runs automatically (no user action required)
- [ ] Profile saved to projects/{id}/voice_profile/
- [ ] Process logged (start, completion, errors)
- [ ] Handles extraction failures gracefully
- [ ] Test integration with transcription workflow

**Notes:**
- Run after transcription to reuse loaded audio
- May take 10-30 seconds depending on model

**Completed:** (date)

---

#### T605: Store Voice Profile in Project Directory
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Low
- **Dependencies:** T604
- **Agent:** (unassigned)
- **Requirements:** FR-20, NFR-6

**Description:**
Persist voice profile to disk for reuse.

**Acceptance Criteria:**
- [ ] Voice profile saved to projects/{id}/voice_profile/embedding.npy (or .json)
- [ ] Metadata saved: extraction_date, model_version, audio_source
- [ ] Profile can be loaded back for TTS generation
- [ ] Test save/load roundtrip
- [ ] Profile file gitignored (in .gitignore)

**Notes:**
- Use numpy.save for embeddings
- Store metadata separately in JSON

**Completed:** (date)

---

#### T606: Implement Text-to-Speech Generation
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** High
- **Dependencies:** T602, T605
- **Agent:** (unassigned)
- **Requirements:** FR-21, FR-22

**Description:**
Generate speech from text using learned voice.

**Acceptance Criteria:**
- [ ] Function: generate_speech(text, voice_profile) -> audio_array
- [ ] Uses TTS model with voice profile
- [ ] Generates intelligible speech
- [ ] Voice resembles original speaker (subjective)
- [ ] Handles short phrases (1-10 words)
- [ ] Test with various text inputs
- [ ] Quality is "good demo quality" (FR-22)

**Notes:**
- XTTS: tts.tts(text, speaker_wav=..., language="en")
- Expect some quality variation

**Completed:** (date)

---

#### T607: Add Prosody Matching Logic
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** High
- **Dependencies:** T606
- **Agent:** (unassigned)
- **Requirements:** FR-22

**Description:**
Approximate prosody (pitch, speed) of surrounding context.

**Acceptance Criteria:**
- [ ] Analyze context tokens for speech rate
- [ ] Adjust generated audio speed to match
- [ ] Optional: match pitch contour (basic)
- [ ] Generated segment sounds natural in context
- [ ] Test with various replacement scenarios
- [ ] Subjective quality check

**Notes:**
- Basic approach: measure syllables/second, time-stretch generated audio
- Advanced: extract pitch from context, apply to TTS
- MVP: simple speed matching is acceptable

**Completed:** (date)

---

#### T608: Create Replacement Endpoint
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T606
- **Agent:** (unassigned)
- **Requirements:** FR-21

**Description:**
Endpoint to trigger audio replacement for edited text.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/replace endpoint
- [ ] Request body: {token_ids: [...], new_text: "..."}
- [ ] Validates token_ids exist
- [ ] Generates replacement audio using TTS
- [ ] Saves generated segment to projects/{id}/generated/
- [ ] Updates segment metadata
- [ ] Returns generated segment metadata
- [ ] Test with curl/Postman

**Notes:**
- Can be async (return task_id) if generation is slow
- Link generated segment to edit operation

**Completed:** (date)

---

#### T609: Handle Text Replacement
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** High
- **Dependencies:** T608
- **Agent:** (unassigned)
- **Requirements:** FR-21, FR-24

**Description:**
Detect changed tokens and trigger audio generation.

**Acceptance Criteria:**
- [ ] Detect token replacement in edit operations
- [ ] Extract old token IDs and new text
- [ ] Call TTS service to generate audio
- [ ] Create new audio segment (source=generated)
- [ ] Link segment to replacement tokens
- [ ] Handle re-generation (user edits same region again)
- [ ] Test various replacement scenarios

**Notes:**
- Replacement means: delete old tokens + insert new text
- Reuse voice profile from project
- If re-generation: replace old generated segment

**Completed:** (date)

---

#### T610: Align Generated Audio to Original Segment
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** High
- **Dependencies:** T609
- **Agent:** (unassigned)
- **Requirements:** FR-21

**Description:**
Match duration of generated audio to original segment.

**Acceptance Criteria:**
- [ ] Measure original segment duration
- [ ] Generate TTS audio
- [ ] If generated audio is shorter/longer, apply time-stretching
- [ ] Time-stretch preserves pitch (use librosa.effects.time_stretch)
- [ ] Acceptable duration tolerance: ±20%
- [ ] Test with various duration mismatches
- [ ] Generated audio sounds natural after stretching

**Notes:**
- Time-stretching has quality limits (>2x sounds bad)
- If mismatch is too large, warn user or adjust context

**Completed:** (date)

---

#### T611: Store Generated Segments
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Low
- **Dependencies:** T609
- **Agent:** (unassigned)
- **Requirements:** FR-23

**Description:**
Save generated audio segments with metadata.

**Acceptance Criteria:**
- [ ] Generated segments saved to projects/{id}/generated/{segment_id}.wav
- [ ] Segment metadata: id, source=generated, start, end, linked_tokens, text, created_at
- [ ] Metadata includes: generation_model, voice_profile_id
- [ ] Segments tracked in project metadata
- [ ] Test save and retrieval

**Notes:**
- Use WAV format for lossless storage
- Include enough metadata for debugging

**Completed:** (date)

---

#### T612: Update AudioRenderer for Mixed Segments
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T505, T611
- **Agent:** (unassigned)
- **Requirements:** FR-16

**Description:**
Enhance AudioRenderer to mix original + generated segments.

**Acceptance Criteria:**
- [ ] Renderer loads both original and generated segments
- [ ] Segments ordered by timeline (start time)
- [ ] Concatenates in correct order
- [ ] Cross-fades applied at all boundaries
- [ ] Test with mix of original and generated segments
- [ ] Output audio is seamless

**Notes:**
- Ensure all segments have same sample rate
- Handle volume normalization across sources

**Completed:** (date)

---

#### T613: Frontend - Trigger Replacement on Text Change
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T402, T608
- **Agent:** (unassigned)
- **Requirements:** FR-21

**Description:**
Automatically trigger TTS when user edits text.

**Acceptance Criteria:**
- [ ] Detect text replacement in editor (token changed)
- [ ] Debounce to avoid excessive requests (e.g., 1 second after typing stops)
- [ ] Send replacement request to backend
- [ ] Show generation in progress (spinner on token)
- [ ] Update UI when generation completes
- [ ] Test typing and editing workflows

**Notes:**
- Use debounce to wait for user to finish typing
- Consider manual "Regenerate" button as alternative

**Completed:** (date)

---

#### T614: Frontend - Show Generation Progress
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T613
- **Agent:** (unassigned)
- **Requirements:** NFR-9

**Description:**
Display progress while generating replacement audio.

**Acceptance Criteria:**
- [ ] Shows "Generating..." indicator on edited token
- [ ] If async: poll for completion status
- [ ] Shows completion or error state
- [ ] Allows playback of generated segment
- [ ] Clear visual feedback (spinner, progress text)
- [ ] Test generation workflow

**Notes:**
- Similar to transcription progress (T311)
- Provide option to cancel generation (optional)

**Completed:** (date)

---

#### T615: Optimize Generation Time
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Medium
- **Dependencies:** T606
- **Agent:** (unassigned)
- **Requirements:** NFR-2

**Description:**
Optimize TTS to meet performance target.

**Acceptance Criteria:**
- [ ] Benchmark: single word generation in <5 seconds
- [ ] Profile TTS pipeline for bottlenecks
- [ ] Optimize: use GPU, reduce model size, cache models
- [ ] Test on target hardware (CPU and GPU)
- [ ] Document performance characteristics
- [ ] Performance notes added to docs/

**Notes:**
- NFR-2 target: <5 sec for short phrase
- GPU significantly faster than CPU
- Consider streaming TTS for real-time (future)

**Completed:** (date)

---

#### T616: Write Tests for Voice Extraction and TTS
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** High
- **Dependencies:** T603, T606
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Test voice cloning pipeline end-to-end.

**Acceptance Criteria:**
- [ ] tests/backend/test_voice_model.py created
- [ ] Test: extract voice profile from sample audio
- [ ] Test: generate speech with profile
- [ ] Test: generated audio is valid (duration, format)
- [ ] Test: handles missing profile error
- [ ] Test: handles invalid text input
- [ ] All tests passing

**Notes:**
- Mock TTS model for unit tests (use fake embeddings)
- Use real model for integration tests (slower)
- Check generated audio with soundfile

**Completed:** (date)

---

#### T617: Quality Check - Generated Voice Resembles Original
- **Status:** Not Started
- **Phase:** 6
- **Complexity:** Low
- **Dependencies:** T616
- **Agent:** (unassigned)
- **Requirements:** FR-22

**Description:**
Subjective quality test for voice similarity.

**Acceptance Criteria:**
- [ ] Generate 5+ test samples with different voices
- [ ] Listen to original vs. generated audio
- [ ] Assess: intelligibility, voice similarity, naturalness
- [ ] Document quality assessment in docs/testing.md
- [ ] Quality meets "good demo quality" standard
- [ ] Identify any common issues (artifacts, mispronunciations)

**Notes:**
- This is subjective, but critical for MVP acceptance
- Get human feedback if possible
- Document known limitations

**Completed:** (date)

---

### Phase 7: Pause Detection & Adjustment

#### T701: Implement Silence Detection Algorithm
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T204
- **Agent:** (unassigned)
- **Requirements:** FR-17

**Description:**
Detect silence segments in audio.

**Acceptance Criteria:**
- [ ] backend/utils/silence_detection.py created
- [ ] Function: detect_silences(audio_path, threshold_db=-40, min_duration=1.0) -> List[{start, end}]
- [ ] Uses RMS or peak amplitude to detect silence
- [ ] Configurable threshold (dB) and minimum duration
- [ ] Returns list of silence intervals
- [ ] Test with sample audio (known silences)

**Notes:**
- Use librosa.effects.split (inverse) or custom algorithm
- Default: detect pauses >1 second

**Completed:** (date)

---

#### T702: Add Configurable Silence Threshold
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Low
- **Dependencies:** T701
- **Agent:** (unassigned)
- **Requirements:** FR-17

**Description:**
Allow configuration of silence detection parameters.

**Acceptance Criteria:**
- [ ] Parameters exposed: threshold_db, min_duration
- [ ] Defaults: threshold=-40dB, min_duration=1.0s
- [ ] Parameters configurable via API or config file
- [ ] Test with different thresholds
- [ ] Document parameter effects

**Notes:**
- Higher threshold = more aggressive silence detection
- Adjust based on audio quality and background noise

**Completed:** (date)

---

#### T703: Insert Pause Tokens in Transcript
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T306, T701
- **Agent:** (unassigned)
- **Requirements:** FR-17

**Description:**
Add pause tokens to transcript for detected silences.

**Acceptance Criteria:**
- [ ] Pause tokens created: {id, text: "[pause 2.3s]", start, end, type: pause}
- [ ] Pause tokens inserted in transcript at correct positions
- [ ] Duration displayed in token text (e.g., 2.3s)
- [ ] Pause tokens sorted with word tokens by timeline
- [ ] Test transcript with pauses

**Notes:**
- Insert pauses during transcription (T307)
- Or as post-processing step after transcription

**Completed:** (date)

---

#### T704: Make Pause Tokens Selectable in Editor
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T403, T703
- **Agent:** (unassigned)
- **Requirements:** FR-18

**Description:**
Render pause tokens as interactive elements in editor.

**Acceptance Criteria:**
- [ ] Pause tokens rendered as: <span class="token-pause">[pause 2.3s]</span>
- [ ] Pause tokens can be clicked/selected
- [ ] Clicking pause token opens adjustment UI
- [ ] Visual styling distinguishes pauses from words
- [ ] Test selection and interaction

**Notes:**
- Use distinct color/background for pause tokens
- Consider using <button> for better interaction

**Completed:** (date)

---

#### T705: Create Pause Adjustment UI
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T704
- **Agent:** (unassigned)
- **Requirements:** FR-18

**Description:**
UI to adjust pause duration.

**Acceptance Criteria:**
- [ ] frontend/src/components/PauseAdjuster.tsx created
- [ ] Shows current pause duration
- [ ] Slider or input field to set new duration (0 - 10 seconds)
- [ ] "Apply" button to submit change
- [ ] Updates backend via API
- [ ] Reflects new duration in transcript
- [ ] Test pause adjustment workflow

**Notes:**
- Display as modal or inline editor
- Validate: duration >= 0
- Optional: "Remove Pause" button (set to 0)

**Completed:** (date)

---

#### T706: Add Pause Modification Endpoint
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T705
- **Agent:** (unassigned)
- **Requirements:** FR-18, FR-19

**Description:**
Endpoint to modify pause duration.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/pause endpoint
- [ ] Request body: {pause_token_id, new_duration}
- [ ] Validates token is a pause type
- [ ] Updates token duration
- [ ] Adjusts audio timeline (T707, T708)
- [ ] Returns updated transcript
- [ ] Test with curl/Postman

**Notes:**
- Duration in seconds (float)
- Validate: new_duration >= 0

**Completed:** (date)

---

#### T707: Implement Silence Trimming
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T706
- **Agent:** (unassigned)
- **Requirements:** FR-19

**Description:**
Reduce pause duration by trimming silence audio.

**Acceptance Criteria:**
- [ ] Function: trim_silence(audio_segment, original_duration, new_duration) -> audio_segment
- [ ] Trims silence from end (or split if symmetric)
- [ ] Preserves audio quality
- [ ] Test with various trim amounts
- [ ] Result duration matches new_duration (within tolerance)

**Notes:**
- If new_duration < original, trim excess
- If trimming entire pause, remove segment

**Completed:** (date)

---

#### T708: Implement Silence Padding
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Low
- **Dependencies:** T706
- **Agent:** (unassigned)
- **Requirements:** FR-19

**Description:**
Extend pause duration by adding silence.

**Acceptance Criteria:**
- [ ] Function: pad_silence(audio_segment, original_duration, new_duration) -> audio_segment
- [ ] Appends zero samples (silence) to extend duration
- [ ] Test with various padding amounts
- [ ] Result duration matches new_duration

**Notes:**
- If new_duration > original, pad with zeros
- Ensure sample rate matches

**Completed:** (date)

---

#### T709: Update AudioRenderer for Adjusted Pauses
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T505, T707, T708
- **Agent:** (unassigned)
- **Requirements:** FR-19

**Description:**
Renderer uses adjusted pause durations.

**Acceptance Criteria:**
- [ ] Renderer checks for pause adjustments
- [ ] Applies trimming or padding as needed
- [ ] Concatenates with adjusted pauses
- [ ] Test with adjusted pauses in timeline
- [ ] Output audio reflects new pause durations

**Notes:**
- Pause adjustment is non-destructive (original audio preserved)
- Apply adjustments during rendering

**Completed:** (date)

---

#### T710: Write Tests for Pause Detection and Adjustment
- **Status:** Not Started
- **Phase:** 7
- **Complexity:** Medium
- **Dependencies:** T701, T707, T708
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Test silence detection and pause modification.

**Acceptance Criteria:**
- [ ] tests/backend/test_silence.py created
- [ ] Test: detect silence in sample audio
- [ ] Test: trim silence to reduce duration
- [ ] Test: pad silence to extend duration
- [ ] Test: handle zero-duration pause (removal)
- [ ] Test: timeline integrity after adjustments
- [ ] All tests passing

**Notes:**
- Create synthetic audio with known silences
- Verify output durations with librosa.get_duration

**Completed:** (date)

---

### Phase 8: Playback Controls & Synchronization

#### T801: Create AudioPlayer React Component
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** High
- **Dependencies:** T003
- **Agent:** (unassigned)
- **Requirements:** FR-25

**Description:**
Build audio player component with standard controls.

**Acceptance Criteria:**
- [ ] frontend/src/components/AudioPlayer.tsx created
- [ ] Uses HTML5 <audio> element or Web Audio API
- [ ] Displays audio source (current project)
- [ ] Provides audio context for playback controls
- [ ] Test component renders and loads audio

**Notes:**
- Web Audio API offers more control but higher complexity
- HTML5 audio is simpler for MVP
- Expose player state via React context or props

**Completed:** (date)

---

#### T802: Implement Play/Pause Controls
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Low
- **Dependencies:** T801
- **Agent:** (unassigned)
- **Requirements:** FR-25

**Description:**
Add play and pause buttons.

**Acceptance Criteria:**
- [ ] Play button starts audio playback
- [ ] Pause button pauses playback
- [ ] Button toggles between play/pause states
- [ ] Keyboard shortcut: Space bar toggles play/pause
- [ ] Visual feedback (button state changes)
- [ ] Test play/pause functionality

**Notes:**
- Use standard play/pause icons
- Prevent default spacebar scroll behavior

**Completed:** (date)

---

#### T803: Add Seek Functionality
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Medium
- **Dependencies:** T802
- **Agent:** (unassigned)
- **Requirements:** FR-25

**Description:**
Progress bar for seeking to any position.

**Acceptance Criteria:**
- [ ] Progress bar shows current playback position
- [ ] Clicking progress bar seeks to that position
- [ ] Dragging progress bar scrubs through audio
- [ ] Seeking updates playback position immediately
- [ ] Progress bar updates smoothly during playback
- [ ] Test seeking with mouse and keyboard

**Notes:**
- Use HTML5 <input type="range"> or custom slider
- Update audio.currentTime on seek

**Completed:** (date)

---

#### T804: Implement Click-to-Play from Transcript
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** High
- **Dependencies:** T404, T802
- **Agent:** (unassigned)
- **Requirements:** FR-12

**Description:**
Clicking word in transcript starts playback from that position.

**Acceptance Criteria:**
- [ ] Clicking a token in editor triggers playback
- [ ] Playback starts at token's start time
- [ ] Player state updates (playing)
- [ ] Progress bar reflects new position
- [ ] Test with various token positions
- [ ] Works with original and generated segments

**Notes:**
- Use token's start_time to set audio.currentTime
- Render audio with AudioRenderer if not cached

**Completed:** (date)

---

#### T805: Add Real-Time Position Indicator in Transcript
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** High
- **Dependencies:** T804
- **Agent:** (unassigned)
- **Requirements:** FR-12, FR-25

**Description:**
Highlight current word during playback.

**Acceptance Criteria:**
- [ ] Current word highlighted (background color or underline)
- [ ] Highlight updates in real-time (sync with audio)
- [ ] Highlight moves smoothly through transcript
- [ ] Uses token timestamps for accuracy
- [ ] Auto-scrolls editor to keep current word visible
- [ ] Test synchronization accuracy

**Notes:**
- Listen to audio.ontimeupdate event
- Find token where start <= currentTime < end
- Add .current-word CSS class

**Completed:** (date)

---

#### T806: Implement Playback Speed Control
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Low
- **Dependencies:** T802
- **Agent:** (unassigned)
- **Requirements:** FR-26

**Description:**
Allow adjusting playback speed.

**Acceptance Criteria:**
- [ ] Speed control buttons or dropdown: 0.75x, 1x, 1.25x, 1.5x
- [ ] Selecting speed adjusts audio.playbackRate
- [ ] Playback continues smoothly at new speed
- [ ] Current speed displayed
- [ ] Test all speed settings
- [ ] Keyboard shortcuts for speed (optional)

**Notes:**
- Use audio.playbackRate property
- Preserve pitch at different speeds (browser default)

**Completed:** (date)

---

#### T807: Add Loop Region Functionality
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Medium
- **Dependencies:** T405, T802
- **Agent:** (unassigned)
- **Requirements:** FR-26

**Description:**
Loop playback of selected text region.

**Acceptance Criteria:**
- [ ] "Loop Selection" button (enabled when text selected)
- [ ] Loops playback between selection start and end times
- [ ] Automatically restarts at end of selection
- [ ] "Stop Loop" button to exit loop mode
- [ ] Test looping various selections
- [ ] Visual feedback (loop active indicator)

**Notes:**
- Listen to audio.ontimeupdate, check if currentTime >= loopEnd
- If true, set currentTime = loopStart

**Completed:** (date)

---

#### T808: Display Current Time and Total Duration
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Low
- **Dependencies:** T801
- **Agent:** (unassigned)
- **Requirements:** FR-25

**Description:**
Show playback time in MM:SS format.

**Acceptance Criteria:**
- [ ] Displays current time (e.g., 1:23)
- [ ] Displays total duration (e.g., 5:00)
- [ ] Format: MM:SS or HH:MM:SS if >1 hour
- [ ] Updates every 100ms during playback
- [ ] Test with various audio durations

**Notes:**
- Use audio.currentTime and audio.duration
- Format with: new Date(seconds * 1000).toISOString().substr(14, 5)

**Completed:** (date)

---

#### T809: Handle Playback of Assembled Audio
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** High
- **Dependencies:** T508, T801
- **Agent:** (unassigned)
- **Requirements:** FR-15, FR-16

**Description:**
Play assembled audio (original + generated + adjusted).

**Acceptance Criteria:**
- [ ] Player loads assembled audio from /api/projects/{id}/preview
- [ ] Playback includes all edits (deletions, replacements, pauses)
- [ ] Playback is seamless (no gaps or clicks)
- [ ] Can switch between original and edited audio (optional)
- [ ] Test with various edit combinations

**Notes:**
- Fetch preview on demand or pre-render and cache
- Consider streaming for large files

**Completed:** (date)

---

#### T810: Synchronize Player State Across Edits
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Medium
- **Dependencies:** T809
- **Agent:** (unassigned)
- **Requirements:** FR-25

**Description:**
Update player when audio is edited.

**Acceptance Criteria:**
- [ ] When edit is made, player reloads assembled audio
- [ ] Playback position preserved if possible (adjust for timeline changes)
- [ ] Duration updates if audio length changed
- [ ] Progress bar reflects new duration
- [ ] Test editing while playing

**Notes:**
- Debounce reload to avoid excessive re-rendering
- Pause playback during edit processing (optional)

**Completed:** (date)

---

#### T811: Write Tests for Playback Logic
- **Status:** Not Started
- **Phase:** 8
- **Complexity:** Medium
- **Dependencies:** T804, T805, T809
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Test playback timing and synchronization.

**Acceptance Criteria:**
- [ ] tests/frontend/AudioPlayer.test.tsx created
- [ ] Test: play/pause controls
- [ ] Test: seek to position
- [ ] Test: click-to-play from transcript
- [ ] Test: current word highlighting
- [ ] Test: playback speed change
- [ ] All tests passing

**Notes:**
- Use React Testing Library
- Mock audio element for unit tests
- Test timing logic with fake timers

**Completed:** (date)

---

### Phase 9: Export Functionality

#### T901: Create AudioExporter Service
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T505
- **Agent:** (unassigned)
- **Requirements:** FR-27, FR-28

**Description:**
Service to export final edited audio to file.

**Acceptance Criteria:**
- [ ] backend/services/audio_exporter.py created
- [ ] Function: export(project_id, format, output_path) -> file_path
- [ ] Renders full audio with AudioRenderer
- [ ] Applies normalization
- [ ] Saves to output file
- [ ] Test export to file

**Notes:**
- Reuse AudioRenderer for segment assembly
- Support WAV and MP3 formats

**Completed:** (date)

---

#### T902: Implement Full Audio Assembly
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T901
- **Agent:** (unassigned)
- **Requirements:** FR-27, FR-28

**Description:**
Assemble all segments into final audio.

**Acceptance Criteria:**
- [ ] Loads all kept and generated segments
- [ ] Concatenates in timeline order
- [ ] Applies cross-fades between segments
- [ ] Handles adjusted pauses
- [ ] Test with complex edits (multiple segment types)
- [ ] Output audio matches expected duration

**Notes:**
- Reuse logic from AudioRenderer (T505)
- Ensure all segments at same sample rate

**Completed:** (date)

---

#### T903: Add Cross-Fading for All Boundaries
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Low
- **Dependencies:** T902
- **Agent:** (unassigned)
- **Requirements:** FR-16

**Description:**
Apply cross-fades at all segment boundaries in export.

**Acceptance Criteria:**
- [ ] Cross-fade duration: 10-50ms
- [ ] Applied at every segment boundary
- [ ] No audible clicks or pops
- [ ] Test export audio quality
- [ ] Compare with preview playback (should match)

**Notes:**
- Reuse cross-fade logic from T507
- Optionally skip fades at natural boundaries

**Completed:** (date)

---

#### T904: Apply Normalization to Prevent Clipping
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T902
- **Agent:** (unassigned)
- **Requirements:** FR-28

**Description:**
Normalize audio levels to prevent clipping.

**Acceptance Criteria:**
- [ ] Peak normalization to -1dB (or -0.1dB for safety)
- [ ] Check for clipping (values > 1.0 or < -1.0)
- [ ] Scale audio if needed
- [ ] Test with various audio levels
- [ ] Exported audio has no clipping artifacts

**Notes:**
- Use librosa or manual scaling: audio = audio / np.max(np.abs(audio)) * 0.99
- Consider RMS normalization for consistent loudness (optional)

**Completed:** (date)

---

#### T905: Support WAV Export
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Low
- **Dependencies:** T904
- **Agent:** (unassigned)
- **Requirements:** FR-27

**Description:**
Export audio as WAV file.

**Acceptance Criteria:**
- [ ] Function: export_wav(audio, output_path, sample_rate)
- [ ] Saves as 16-bit PCM WAV
- [ ] File can be played in standard audio players
- [ ] Test WAV export
- [ ] Validate file format with soundfile

**Notes:**
- Use soundfile.write(output_path, audio, sample_rate, subtype='PCM_16')
- WAV is lossless, good for quality

**Completed:** (date)

---

#### T906: Support MP3 Export
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T904
- **Agent:** (unassigned)
- **Requirements:** FR-27

**Description:**
Export audio as MP3 file.

**Acceptance Criteria:**
- [ ] Function: export_mp3(audio, output_path, sample_rate, bitrate=192)
- [ ] Uses LAME encoder or pydub for conversion
- [ ] File can be played in standard audio players
- [ ] Bitrate configurable (default 192kbps)
- [ ] Test MP3 export
- [ ] Validate file format

**Notes:**
- Use pydub: AudioSegment(...).export(output_path, format="mp3", bitrate="192k")
- MP3 is lossy but smaller file size

**Completed:** (date)

---

#### T907: Add Export Endpoint
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T905, T906
- **Agent:** (unassigned)
- **Requirements:** FR-27

**Description:**
Endpoint to trigger audio export.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/export endpoint
- [ ] Request body: {format: "wav" | "mp3"}
- [ ] Starts export task (async)
- [ ] Returns task_id (202 Accepted)
- [ ] Export file saved to projects/{id}/exports/
- [ ] Test with curl/Postman

**Notes:**
- Export can take 1-2 minutes, make it async
- Cleanup old exports to save disk space (optional)

**Completed:** (date)

---

#### T908: Handle Export as Background Task
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T907
- **Agent:** (unassigned)
- **Requirements:** NFR-3

**Description:**
Run export in background with progress tracking.

**Acceptance Criteria:**
- [ ] Export runs in background thread/task
- [ ] GET /api/projects/{id}/export/status returns progress
- [ ] Status: queued, processing, completed, failed
- [ ] Optional: progress percentage
- [ ] Completed export available for download
- [ ] Test status polling

**Notes:**
- Similar to transcription task (T308)
- Store task state in memory or database

**Completed:** (date)

---

#### T909: Create Export UI with Format Selection
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Low
- **Dependencies:** T003, T907
- **Agent:** (unassigned)
- **Requirements:** FR-27, NFR-9

**Description:**
UI to select export format and trigger export.

**Acceptance Criteria:**
- [ ] frontend/src/components/ExportModal.tsx created
- [ ] Radio buttons or dropdown for format (WAV, MP3)
- [ ] "Export" button triggers POST /api/projects/{id}/export
- [ ] Shows loading state while exporting
- [ ] Disabled if no edits made (optional)
- [ ] Test export workflow

**Notes:**
- Display as modal or dedicated export section
- Clear labels and instructions

**Completed:** (date)

---

#### T910: Display Export Progress and Download Link
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T908, T909
- **Agent:** (unassigned)
- **Requirements:** NFR-9

**Description:**
Show export progress and provide download link.

**Acceptance Criteria:**
- [ ] Polls GET /api/projects/{id}/export/status
- [ ] Shows status: "Queued", "Exporting...", "Ready", "Failed"
- [ ] Optional: progress bar
- [ ] On completion: download link appears
- [ ] Download link: GET /api/projects/{id}/export/download
- [ ] Test download functionality

**Notes:**
- Use anchor tag with download attribute
- Provide filename: project_{id}_edited.wav

**Completed:** (date)

---

#### T911: Optional - Export Transcript as TXT/JSON
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Low
- **Dependencies:** T306
- **Agent:** (unassigned)
- **Requirements:** FR-27 (optional)

**Description:**
Allow exporting transcript as text or JSON file.

**Acceptance Criteria:**
- [ ] POST /api/projects/{id}/export/transcript endpoint
- [ ] Request body: {format: "txt" | "json"}
- [ ] TXT: plain text reconstruction
- [ ] JSON: full transcript with timestamps
- [ ] Returns file for download
- [ ] Test transcript export

**Notes:**
- Nice-to-have for MVP, can defer if time-constrained
- Useful for documentation or subtitles

**Completed:** (date)

---

#### T912: Optimize Export Performance
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T902, T908
- **Agent:** (unassigned)
- **Requirements:** NFR-3

**Description:**
Optimize export to meet performance target.

**Acceptance Criteria:**
- [ ] Benchmark: 5-minute audio exports in <2 minutes
- [ ] Profile export pipeline for bottlenecks
- [ ] Optimize: reduce I/O, parallelize if possible
- [ ] Test on target hardware
- [ ] Document performance characteristics

**Notes:**
- NFR-3 target: ~1-2 min for 5 min audio
- Most time spent in rendering and encoding

**Completed:** (date)

---

#### T913: Write Tests for Export Quality
- **Status:** Not Started
- **Phase:** 9
- **Complexity:** Medium
- **Dependencies:** T905, T906
- **Agent:** (unassigned)
- **Requirements:** Testing standards

**Description:**
Test export output for quality and correctness.

**Acceptance Criteria:**
- [ ] tests/backend/test_export.py created
- [ ] Test: export WAV, validate format
- [ ] Test: export MP3, validate format
- [ ] Test: exported audio has correct duration
- [ ] Test: exported audio has no clipping
- [ ] Test: exported audio includes all edits
- [ ] All tests passing

**Notes:**
- Use soundfile and pydub to validate output files
- Compare expected vs. actual duration

**Completed:** (date)

---

### Phase 10: Polish, Testing & Documentation

#### T1001: End-to-End Integration Testing
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** High
- **Dependencies:** All previous phases
- **Agent:** (unassigned)
- **Requirements:** All FRs

**Description:**
Test complete user workflow from upload to export.

**Acceptance Criteria:**
- [ ] tests/integration/test_full_workflow.py created
- [ ] Test: upload audio → transcribe → edit → delete → replace → adjust pause → play → export
- [ ] Test: all steps complete without errors
- [ ] Test: exported audio matches expected result
- [ ] Test: can load saved project and resume
- [ ] All tests passing

**Notes:**
- Use realistic sample audio (2-5 minutes)
- Automate as much as possible, manual verification for quality

**Completed:** (date)

---

#### T1002: Performance Testing
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** T313, T615, T912
- **Agent:** (unassigned)
- **Requirements:** NFR-1, NFR-2, NFR-3

**Description:**
Measure actual performance against targets.

**Acceptance Criteria:**
- [ ] Benchmark suite created: tests/performance/
- [ ] Test: transcription time for 2min, 5min, 10min audio
- [ ] Test: TTS generation time for 1 word, 5 words, 10 words
- [ ] Test: export time for 2min, 5min, 10min audio
- [ ] Results documented in docs/performance.md
- [ ] All NFR targets met or documented if not

**Notes:**
- Run on target hardware (document specs)
- CPU vs GPU performance comparison

**Completed:** (date)

---

#### T1003: Error Handling Review
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** All previous phases
- **Agent:** (unassigned)
- **Requirements:** NFR-10

**Description:**
Review all error paths for user-friendly messages.

**Acceptance Criteria:**
- [ ] Audit all API endpoints for error responses
- [ ] Ensure all errors have clear messages (NFR-10)
- [ ] Test: file too large, unsupported format, file not found, etc.
- [ ] Frontend displays all error messages correctly
- [ ] No stack traces or internal errors shown to user
- [ ] Error handling checklist completed

**Notes:**
- Use examples from NFR-10: "This file is too long..."
- Add error handling where missing

**Completed:** (date)

---

#### T1004: UI Polish
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** All frontend tasks
- **Agent:** (unassigned)
- **Requirements:** NFR-9

**Description:**
Polish UI for consistency and usability.

**Acceptance Criteria:**
- [ ] Consistent styling across all components
- [ ] Responsive layout (works on different screen sizes)
- [ ] Loading states for all async operations
- [ ] Clear visual feedback for all user actions
- [ ] Accessible (keyboard navigation, screen reader friendly)
- [ ] Visual design review completed

**Notes:**
- Use CSS framework or custom styles
- Focus on clarity over fancy design (MVP)

**Completed:** (date)

---

#### T1005: Add Tooltips and Onboarding Hints
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** T1004
- **Agent:** (unassigned)
- **Requirements:** NFR-9

**Description:**
Add helpful hints for first-time users.

**Acceptance Criteria:**
- [ ] Tooltips on buttons and controls
- [ ] Onboarding flow: "1. Upload or Record", "2. Generate Transcript", etc.
- [ ] Help icon with usage instructions (optional)
- [ ] First-run tutorial or tour (optional)
- [ ] Test with new user (if possible)

**Notes:**
- Keep it minimal, non-intrusive
- Use popovers or tooltips library

**Completed:** (date)

---

#### T1006: Create Sample Audio Files
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** None
- **Agent:** (unassigned)
- **Requirements:** Testing

**Description:**
Generate synthetic sample audio for testing.

**Acceptance Criteria:**
- [ ] samples/ directory created
- [ ] Sample audio files: 2min, 5min (mono, 16kHz)
- [ ] Audio contains speech (synthetic or recorded)
- [ ] Samples added to .gitignore (if >1MB)
- [ ] README in samples/ explains usage

**Notes:**
- Use TTS or record dummy audio
- Avoid real user data (privacy)

**Completed:** (date)

---

#### T1007: Write Comprehensive README.md
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** T007, T1006
- **Agent:** (unassigned)
- **Requirements:** Documentation

**Description:**
Update README with complete setup and usage instructions.

**Acceptance Criteria:**
- [ ] README includes: project overview, features, MVP scope
- [ ] Prerequisites: Python 3.10+, Node 18+, hardware requirements
- [ ] Installation: step-by-step setup for backend and frontend
- [ ] Running the app: `make dev` or manual commands
- [ ] Usage guide: upload, transcribe, edit, export
- [ ] Troubleshooting: common issues and solutions
- [ ] Screenshots or GIFs (optional)
- [ ] Links to other docs: requirements.md, AI.md, etc.

**Notes:**
- Keep it beginner-friendly
- Use code blocks for commands

**Completed:** (date)

---

#### T1008: Document API Endpoints in OpenAPI/Swagger
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** All backend tasks
- **Agent:** (unassigned)
- **Requirements:** Documentation

**Description:**
Generate API documentation using OpenAPI.

**Acceptance Criteria:**
- [ ] FastAPI auto-generates OpenAPI spec
- [ ] All endpoints documented with descriptions
- [ ] Request/response schemas included
- [ ] Swagger UI accessible at /docs
- [ ] ReDoc accessible at /redoc (optional)
- [ ] API documentation reviewed for accuracy

**Notes:**
- FastAPI provides this automatically
- Add docstrings to endpoints for better docs

**Completed:** (date)

---

#### T1009: Create CONTRIBUTING.md
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** T007
- **Agent:** (unassigned)
- **Requirements:** Documentation

**Description:**
Document contribution guidelines for future developers.

**Acceptance Criteria:**
- [ ] CONTRIBUTING.md created
- [ ] Includes: code style, testing requirements, PR process
- [ ] Links to AGENTS.md, AI.md
- [ ] Conventional commits explained
- [ ] How to report issues
- [ ] Code of conduct (optional)

**Notes:**
- Adapt from AGENTS.md content
- Keep it concise for MVP

**Completed:** (date)

---

#### T1010: Security Review
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** All backend tasks
- **Agent:** (unassigned)
- **Requirements:** NFR-6, NFR-7, NFR-8

**Description:**
Review code for security vulnerabilities.

**Acceptance Criteria:**
- [ ] Input validation review (file uploads, API parameters)
- [ ] No path traversal vulnerabilities
- [ ] No command injection (sanitize filenames)
- [ ] No sensitive data in logs (NFR-8)
- [ ] No hardcoded secrets or credentials
- [ ] Security checklist completed

**Notes:**
- Use OWASP top 10 as reference
- Run security linter (e.g., bandit for Python)

**Completed:** (date)

---

#### T1011: Privacy Audit
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** All tasks
- **Agent:** (unassigned)
- **Requirements:** NFR-6, NFR-7, NFR-8

**Description:**
Verify compliance with privacy requirements.

**Acceptance Criteria:**
- [ ] All audio files stored locally only (NFR-6)
- [ ] No external telemetry or analytics (NFR-7)
- [ ] No audio/transcript content in logs (NFR-8)
- [ ] No third-party data uploads (unless explicitly documented)
- [ ] Privacy audit checklist completed

**Notes:**
- Review all network calls (should be none for MVP)
- Document any future cloud integration as opt-in

**Completed:** (date)

---

#### T1012: Cross-Platform Testing
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Medium
- **Dependencies:** All tasks
- **Agent:** (unassigned)
- **Requirements:** NFR-4

**Description:**
Test on Windows, Mac, Linux if possible.

**Acceptance Criteria:**
- [ ] Test on at least 2 platforms (e.g., Windows + Linux)
- [ ] Installation works on all platforms
- [ ] All core features work on all platforms
- [ ] Document platform-specific issues
- [ ] Platform compatibility table in README

**Notes:**
- Use WSL for Linux testing on Windows
- Test with Docker as alternative (optional)

**Completed:** (date)

---

#### T1013: Create Quick-Start Guide with Screenshots
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** T1007
- **Agent:** (unassigned)
- **Requirements:** Documentation

**Description:**
Visual guide for first-time users.

**Acceptance Criteria:**
- [ ] docs/quickstart.md created
- [ ] Screenshots of main UI states (upload, transcript, editing, export)
- [ ] Step-by-step workflow with images
- [ ] Clear captions explaining each step
- [ ] Linked from README.md

**Notes:**
- Use sample audio for screenshots
- Keep images optimized (<500KB each)

**Completed:** (date)

---

#### T1014: Final Code Cleanup
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** All tasks
- **Agent:** (unassigned)
- **Requirements:** Code quality

**Description:**
Clean up code before release.

**Acceptance Criteria:**
- [ ] Remove debug print statements
- [ ] Remove commented-out code
- [ ] Resolve all TODOs or document as future work
- [ ] Run linters and fix issues (`make lint`)
- [ ] Run formatters (`make fmt`)
- [ ] Code reviewed for clarity

**Notes:**
- Use `grep -r "TODO" .` to find remaining TODOs
- Remove or document them

**Completed:** (date)

---

#### T1015: Update TASKBOARD.md to Mark Complete
- **Status:** Not Started
- **Phase:** 10
- **Complexity:** Low
- **Dependencies:** T1001-T1014
- **Agent:** (unassigned)
- **Requirements:** Project management

**Description:**
Final update to taskboard marking project complete.

**Acceptance Criteria:**
- [ ] All tasks status updated to "Done"
- [ ] Progress table shows 100% completion
- [ ] Final review of task completion
- [ ] TASKBOARD.md archived or marked as v1.0

**Notes:**
- This is the final task in the MVP workplan
- Celebrate completion!

**Completed:** (date)

---

## 5. Agent Notes

### General Guidelines for AI Agents

1. **Always read task dependencies first** - Don't start a task until its dependencies are complete.

2. **Update status immediately** - When you start a task, update its status to "In Progress" in this file.

3. **Follow acceptance criteria strictly** - Don't mark a task done until ALL criteria are met.

4. **Test as you go** - Write and run tests for each task before marking complete.

5. **Document blockers** - If blocked, update status and add detailed notes explaining why.

6. **Commit frequently** - Use conventional commits (feat:, fix:, etc.) as per AGENTS.md.

7. **Ask for clarification** - If requirements are unclear, document questions in task notes.

8. **Preserve user privacy** - Never log or expose audio content or transcripts (NFR-8).

9. **Keep it simple** - MVP scope only, avoid feature creep unless explicitly approved.

10. **Reference requirements** - Always map work back to requirements.md specifications.

### Quality Gates Before Marking "Done"

- [ ] Code written and tested
- [ ] All acceptance criteria met
- [ ] Tests passing (`make test`)
- [ ] Linting passing (`make lint`)
- [ ] Code formatted (`make fmt`)
- [ ] Committed with conventional commit message
- [ ] Task status updated in TASKBOARD.md
- [ ] Documentation updated (if applicable)

---

## 6. Troubleshooting

**Common Issues:**

- **Blocked task:** Check dependencies, ensure prerequisite tasks are complete.
- **Test failures:** Review acceptance criteria, check test setup.
- **Performance issues:** Profile code, optimize bottlenecks, consider hardware limitations.
- **Integration errors:** Verify API contracts, check request/response formats.

**Getting Help:**

- Review requirements.md for specifications
- Check AI.md for behavioral guidelines
- Consult AGENTS.md for coding standards
- Ask human project owner for ambiguities

---

## 7. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-15 | Initial taskboard created with all 119 tasks | AI Agent |

---

**Next Steps:**
1. Review this taskboard and WORKPLAN.md
2. Begin with Phase 0, Task T001
3. Update task status as work progresses
4. Follow the methodology through to completion

**Project Definition of Done:**
- All 119 tasks marked "Done"
- All acceptance criteria met
- All tests passing
- Documentation complete
- Human review and approval obtained
