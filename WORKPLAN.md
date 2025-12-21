# WORKPLAN.md

## 1. Purpose & Overview

This document provides a **comprehensive, methodical workplan** for AI agents to implement the TextAudio Edit MVP from start to finish.

**How to use this workplan:**
1. AI agents should work through phases sequentially (Phase 0 → Phase 10)
2. Within each phase, complete tasks in the order listed (respecting dependencies)
3. Mark tasks as complete only when acceptance criteria are met
4. Reference the TASKBOARD.md for detailed task tracking
5. Consult requirements.md for authoritative specifications
6. Follow AI.md guidelines for coding standards and behavior

**Project Goal:**
Build a local web/desktop application that allows a single user to edit audio by editing a transcript, with AI-powered voice replacement for changed words.

**Target MVP Scope:**
- Single user, local deployment
- Single speaker, English audio
- 2-10 minute recordings
- Text-based editing interface
- Voice learning from sample
- Export edited audio

---

## 2. Prerequisites & Environment Setup

Before starting Phase 0, ensure:
- [ ] Git repository initialized
- [ ] requirements.md, AI.md, AGENTS.md reviewed and understood
- [ ] Development machine meets minimum specs (reasonable CPU, 8GB+ RAM)
- [ ] Internet access for downloading dependencies and models

---

## 3. Technology Stack Assumptions

**Default stack** (can be adjusted but document changes):
- **Backend:** Python 3.10+ with FastAPI
- **Frontend:** React 18+ with Vite and TypeScript
- **ASR Model:** Whisper (openai/whisper or faster-whisper)
- **Voice Cloning:** TTS model with voice cloning capability (e.g., Coqui TTS, XTTS)
- **Audio Processing:** librosa, pydub, soundfile
- **Storage:** Local file system (JSON for metadata)
- **Development:** Docker optional for model isolation

---

## 4. Phase Breakdown

### Phase 0: Project Scaffolding & Setup
**Goal:** Create foundational project structure, tooling, and documentation

**Tasks:**
- **T001:** Create directory structure (`backend/`, `frontend/`, `tests/`, `scripts/`, `docs/`, `samples/`)
- **T002:** Set up Python virtual environment and requirements.txt
- **T003:** Initialize frontend with Vite + React + TypeScript
- **T004:** Create .gitignore (exclude venv, node_modules, audio files, model weights)
- **T005:** Set up code formatting tools (black, ruff for Python; prettier, eslint for TS)
- **T006:** Create Makefile with common commands (fmt, lint, test, dev)
- **T007:** Write initial README.md with setup instructions
- **T008:** Create TASKBOARD.md for task tracking

**Acceptance Criteria:**
- Directory structure exists and is documented
- `make dev` can launch placeholder backend and frontend
- All linting/formatting tools are configured and working
- TASKBOARD.md is initialized with all tasks from this workplan

**Dependencies:** None
**Estimated Complexity:** Low
**Requirements Mapping:** NFR-4 (local deployment)

---

### Phase 1: Backend Core Infrastructure
**Goal:** Implement backend API foundation with project management

**Tasks:**
- **T101:** Create FastAPI application skeleton with CORS configuration
- **T102:** Implement project data model (Project class with id, audio_path, transcript, edits)
- **T103:** Create ProjectManager service for CRUD operations
- **T104:** Implement file storage utilities (save/load audio, manage project folders)
- **T105:** Create REST endpoints: POST /api/projects, GET /api/projects/{id}
- **T106:** Add request/response validation with Pydantic models
- **T107:** Implement error handling middleware and structured error responses
- **T108:** Add basic logging configuration (local file, no audio/transcript logging)
- **T109:** Write unit tests for ProjectManager and file utilities

**Acceptance Criteria:**
- Backend server starts on localhost:8000
- Can create a project and receive a project ID
- Can retrieve project metadata by ID
- All endpoints return proper JSON with error codes
- Tests pass with >80% coverage for core services

**Dependencies:** Phase 0
**Estimated Complexity:** Medium
**Requirements Mapping:** FR-1, FR-2, NFR-4, NFR-8

---

### Phase 2: Audio Input & Validation
**Goal:** Handle audio upload, recording, and format validation

**Tasks:**
- **T201:** Implement audio upload endpoint: POST /api/projects/{id}/upload
- **T202:** Add audio format validation (WAV, MP3) and conversion utilities
- **T203:** Implement duration check (reject files >10 minutes) - FR-4
- **T204:** Normalize audio to mono, consistent sample rate (16kHz or 24kHz)
- **T205:** Store original audio in project directory structure
- **T206:** Create frontend file upload component with drag-and-drop
- **T207:** Implement browser-based audio recording (MediaRecorder API)
- **T208:** Add recording UI with start/stop/playback preview
- **T209:** Display upload progress and validation errors in UI
- **T210:** Write integration tests for upload and validation logic

**Acceptance Criteria:**
- Can upload WAV and MP3 files via API
- Files >10 minutes are rejected with clear error message
- Audio is normalized to mono, 16kHz consistently
- Frontend shows upload progress and handles errors gracefully
- Can record audio directly in browser and save to project
- Tests cover format validation and edge cases

**Dependencies:** Phase 1
**Estimated Complexity:** Medium
**Requirements Mapping:** FR-3, FR-4, FR-5, NFR-10

---

### Phase 3: Automatic Speech Recognition (Transcription)
**Goal:** Implement ASR with word-level timestamps

**Tasks:**
- **T301:** Research and select ASR model (Whisper recommended)
- **T302:** Create TranscriptionService interface/abstract class
- **T303:** Implement WhisperTranscriptionService with local model loading
- **T304:** Add model download/initialization on first run
- **T305:** Implement word-level timestamp extraction from ASR output
- **T306:** Create Transcript data model (list of Token: id, text, start, end, type)
- **T307:** Add transcription endpoint: POST /api/projects/{id}/transcribe
- **T308:** Handle transcription progress/status polling (long-running operation)
- **T309:** Store transcript JSON in project directory
- **T310:** Create frontend component to trigger transcription and show progress
- **T311:** Display transcription status (queued, processing, completed, error)
- **T312:** Write tests with sample audio files (create synthetic test audio)
- **T313:** Measure and optimize transcription performance (target <2min for 5min audio)

**Acceptance Criteria:**
- ASR model downloads and initializes on first use
- Transcription returns word-level timestamps with <100ms precision
- Transcription endpoint handles 5-minute audio in <2 minutes
- Frontend shows real-time transcription progress
- Transcript is saved and can be retrieved
- English audio is accurately transcribed (subjective quality check)
- Tests validate timestamp accuracy and format

**Dependencies:** Phase 2
**Estimated Complexity:** High
**Requirements Mapping:** FR-6, FR-7, FR-8, FR-9, NFR-1

---

### Phase 4: Text Editor & Token Mapping
**Goal:** Build transcript editor with audio-token synchronization

**Tasks:**
- **T401:** Design token-to-audio mapping data structure
- **T402:** Create TranscriptEditor React component (editable text area)
- **T403:** Render transcript from token list with word-level spans
- **T404:** Implement cursor position to token ID mapping
- **T405:** Add text selection to token range mapping
- **T406:** Implement edit tracking (insertions, deletions, replacements)
- **T407:** Create EditOperation data model (type, position, old_tokens, new_text)
- **T408:** Add edit submission endpoint: POST /api/projects/{id}/edit
- **T409:** Implement undo/redo functionality for text edits
- **T410:** Add visual highlighting for edited regions (show what's original vs. generated)
- **T411:** Maintain token mapping integrity after edits (re-index, adjust times)
- **T412:** Write tests for edit operations and token mapping logic

**Acceptance Criteria:**
- Transcript displays as editable text with word boundaries
- Each word can be selected and mapped to its audio timestamp
- Text edits create EditOperation records with proper metadata
- Undo/redo works correctly (at least 10 levels)
- Edited regions are visually distinct from original
- Token mapping updates correctly after insertions/deletions
- Tests cover edge cases (delete all, insert at start/end, etc.)

**Dependencies:** Phase 3
**Estimated Complexity:** High
**Requirements Mapping:** FR-10, FR-11, FR-13

---

### Phase 5: Text-Based Deletion → Audio Editing
**Goal:** Implement audio removal based on text deletions

**Tasks:**
- **T501:** Create AudioSegmentManager service to track active segments
- **T502:** Implement segment marking (kept, removed, generated)
- **T503:** Add deletion handler: map deleted tokens to audio segments
- **T504:** Update project metadata to track removed segments
- **T505:** Create AudioRenderer service for playback assembly
- **T506:** Implement segment concatenation logic (skip removed segments)
- **T507:** Add basic cross-fade at segment boundaries (10-50ms) to avoid clicks
- **T508:** Create playback preview endpoint: GET /api/projects/{id}/preview
- **T509:** Frontend: update editor to show deletion effects in real-time
- **T510:** Frontend: add "preview edit" button to test playback before export
- **T511:** Write tests for segment marking and concatenation logic

**Acceptance Criteria:**
- Deleting text in editor marks corresponding audio as removed
- Playback skips removed segments smoothly
- No audible clicks/pops at deletion boundaries
- Preview endpoint returns assembled audio stream
- Frontend shows deleted text with strikethrough or graying
- Tests verify correct segment boundaries and timing

**Dependencies:** Phase 4
**Estimated Complexity:** Medium
**Requirements Mapping:** FR-14, FR-15, FR-16

---

### Phase 6: Voice Learning & TTS Replacement
**Goal:** Implement voice cloning and audio replacement for edited text

**Tasks:**
- **T601:** Research and select voice cloning TTS model (Coqui XTTS or similar)
- **T602:** Create VoiceModelService interface/abstract class
- **T603:** Implement voice embedding extraction from reference audio
- **T604:** Add automatic voice profile generation after transcription
- **T605:** Store voice profile/embedding in project directory
- **T606:** Implement text-to-speech generation with learned voice
- **T607:** Add prosody matching logic (basic pitch/speed approximation)
- **T608:** Create replacement endpoint: POST /api/projects/{id}/replace
- **T609:** Handle text replacement: detect changed tokens, generate new audio
- **T610:** Align generated audio duration to original segment (time-stretch if needed)
- **T611:** Store generated segments separately with metadata (source=generated)
- **T612:** Update AudioRenderer to mix original + generated segments
- **T613:** Frontend: trigger replacement on text change (with debounce)
- **T614:** Frontend: show generation progress and playback of replaced segment
- **T615:** Optimize generation time (target <5 seconds for single word)
- **T616:** Write tests for voice extraction and TTS generation
- **T617:** Quality check: generated voice resembles original (subjective test)

**Acceptance Criteria:**
- Voice profile is automatically extracted from uploaded audio
- Editing a word triggers TTS generation in learned voice
- Generated audio quality is "good demo quality" (intelligible, recognizable)
- Generation completes in <5 seconds for short phrases
- Playback seamlessly mixes original and generated segments
- Can re-generate if user edits same segment again
- Tests validate embedding extraction and TTS pipeline

**Dependencies:** Phase 5
**Estimated Complexity:** Very High
**Requirements Mapping:** FR-20, FR-21, FR-22, FR-23, FR-24, NFR-2

---

### Phase 7: Pause Detection & Adjustment
**Goal:** Detect silences and allow duration adjustment

**Tasks:**
- **T701:** Implement silence detection algorithm (amplitude threshold + duration)
- **T702:** Add configurable silence threshold (default >1.0 second)
- **T703:** Insert pause tokens in transcript: [pause X.Xs]
- **T704:** Make pause tokens selectable and editable in TranscriptEditor
- **T705:** Create pause adjustment UI (slider or input field for duration)
- **T706:** Add pause modification endpoint: POST /api/projects/{id}/pause
- **T707:** Implement silence trimming (reduce pause duration)
- **T708:** Implement silence padding (extend pause duration)
- **T709:** Update AudioRenderer to respect adjusted pause durations
- **T710:** Write tests for silence detection and adjustment logic

**Acceptance Criteria:**
- Pauses >1 second are detected and marked in transcript
- User can click on [pause 2.3s] and adjust to new duration
- Adjusting pause updates the audio timeline correctly
- Playback reflects new pause durations
- Can both trim (reduce) and extend pauses
- Tests cover edge cases (very short audio, no pauses, etc.)

**Dependencies:** Phase 6
**Estimated Complexity:** Medium
**Requirements Mapping:** FR-17, FR-18, FR-19

---

### Phase 8: Playback Controls & Synchronization
**Goal:** Implement audio player with transcript synchronization

**Tasks:**
- **T801:** Create AudioPlayer React component with HTML5 audio or Web Audio API
- **T802:** Implement play/pause controls
- **T803:** Add seek functionality (progress bar)
- **T804:** Implement click-to-play from transcript (jump to token timestamp)
- **T805:** Add real-time playback position indicator in transcript (highlight current word)
- **T806:** Implement playback speed control (0.75x, 1x, 1.25x, 1.5x)
- **T807:** Add loop region functionality (select text, loop playback)
- **T808:** Display current time and total duration
- **T809:** Handle playback of assembled audio (original + generated + adjusted)
- **T810:** Synchronize player state across edits (update duration when segments change)
- **T811:** Write tests for playback timing and synchronization logic

**Acceptance Criteria:**
- Play/pause/seek controls work smoothly
- Clicking a word in transcript starts playback from that position
- Current word is highlighted during playback
- Playback speed can be adjusted (4 preset speeds)
- Loop region plays selected text repeatedly
- Playback reflects all edits (deletions, replacements, pause adjustments)
- Tests verify timing accuracy and synchronization

**Dependencies:** Phase 7
**Estimated Complexity:** Medium
**Requirements Mapping:** FR-12, FR-25, FR-26

---

### Phase 9: Export Functionality
**Goal:** Export final edited audio to file

**Tasks:**
- **T901:** Create AudioExporter service for final rendering
- **T902:** Implement full audio assembly (all segments in sequence)
- **T903:** Add cross-fading between all segment boundaries
- **T904:** Apply normalization to prevent clipping (peak normalize to -1dB)
- **T905:** Support WAV export (16-bit PCM)
- **T906:** Support MP3 export (using LAME encoder or similar)
- **T907:** Add export endpoint: POST /api/projects/{id}/export
- **T908:** Handle export as long-running background task with progress
- **T909:** Create export UI with format selection (WAV/MP3)
- **T910:** Display export progress and download link when complete
- **T911:** Optional: export transcript as .txt or .json file
- **T912:** Optimize export performance (target <2 minutes for 5-minute audio)
- **T913:** Write tests for export quality and format validation

**Acceptance Criteria:**
- Can export edited audio as WAV or MP3
- Exported audio has all edits applied (deletions, replacements, pauses)
- No clipping or distortion in exported file
- Export completes in <2 minutes for 5-minute source
- Frontend shows export progress bar
- Exported file can be downloaded and played in external player
- Tests verify file format and audio integrity

**Dependencies:** Phase 8
**Estimated Complexity:** Medium
**Requirements Mapping:** FR-27, FR-28, NFR-3

---

### Phase 10: Polish, Testing & Documentation
**Goal:** Final integration, comprehensive testing, and user documentation

**Tasks:**
- **T1001:** End-to-end integration testing (full workflow: upload → transcribe → edit → export)
- **T1002:** Performance testing (measure actual times for 2min, 5min, 10min audio)
- **T1003:** Error handling review (all error paths return user-friendly messages)
- **T1004:** UI polish (consistent styling, responsive layout, loading states)
- **T1005:** Add helpful tooltips and onboarding hints ("1. Upload or Record", etc.)
- **T1006:** Create sample audio files for testing (synthetic, 2-5 minutes)
- **T1007:** Write comprehensive README.md (installation, usage, troubleshooting)
- **T1008:** Document API endpoints in OpenAPI/Swagger format
- **T1009:** Create CONTRIBUTING.md with development guidelines
- **T1010:** Security review (ensure no audio/transcript leakage, validate inputs)
- **T1011:** Privacy audit (confirm NFR-6, NFR-7, NFR-8 compliance)
- **T1012:** Cross-platform testing (test on Windows, Mac, Linux if possible)
- **T1013:** Create quick-start guide with screenshots
- **T1014:** Final code cleanup (remove debug prints, TODOs, commented code)
- **T1015:** Update TASKBOARD.md to mark all tasks complete

**Acceptance Criteria:**
- All critical user paths work end-to-end without errors
- Performance meets NFR targets (transcription <2min, TTS <5sec, export <2min)
- All error messages are clear and actionable (NFR-10)
- UI is intuitive for first-time users (NFR-9)
- No audio or transcripts are logged or leaked (NFR-6, NFR-7, NFR-8)
- Documentation is complete and accurate
- Code passes all linting and formatting checks
- Test coverage >80% for critical paths
- All tasks in TASKBOARD.md are marked "Done"

**Dependencies:** Phase 9
**Estimated Complexity:** Medium
**Requirements Mapping:** All NFRs, general quality

---

## 5. Agent Execution Guidelines

### 5.1 Task Execution Protocol

When working on a task:

1. **Pre-task checklist:**
   - [ ] Read task description and acceptance criteria in TASKBOARD.md
   - [ ] Verify all dependencies are complete
   - [ ] Review relevant sections of requirements.md
   - [ ] Update task status to "In Progress" in TASKBOARD.md

2. **During task:**
   - [ ] Follow coding standards from AGENTS.md
   - [ ] Write tests alongside implementation code
   - [ ] Document non-obvious logic with comments
   - [ ] Run linting and formatting before committing
   - [ ] Test locally to verify acceptance criteria

3. **Post-task checklist:**
   - [ ] All acceptance criteria met
   - [ ] Tests written and passing
   - [ ] Code reviewed (self-review or peer if available)
   - [ ] Documentation updated (if applicable)
   - [ ] Update task status to "Done" in TASKBOARD.md
   - [ ] Commit with conventional commit message (feat:, fix:, etc.)

### 5.2 When Blocked

If a task cannot be completed:
1. Update task status to "Blocked" in TASKBOARD.md
2. Document the blocker in task notes
3. Ask clarifying questions or request human review
4. If possible, work on non-dependent tasks from later phases

### 5.3 Testing Strategy

- **Unit tests:** Test individual functions/classes in isolation
- **Integration tests:** Test API endpoints and service interactions
- **End-to-end tests:** Test full user workflows (manual or automated)
- **Performance tests:** Measure timing against NFR targets
- **Regression tests:** Add tests for any bugs discovered and fixed

### 5.4 Code Quality Gates

Before marking a task as "Done":
- [ ] `make lint` passes with no errors
- [ ] `make fmt` applied
- [ ] `make test` passes with no failures
- [ ] Manual smoke test completed
- [ ] No console errors or warnings in browser (for frontend)
- [ ] No hardcoded secrets or sensitive data

---

## 6. Risk Management & Contingencies

### 6.1 Known Risks

| Risk | Mitigation |
|------|------------|
| ASR model too slow on target hardware | Use faster-whisper or quantized models; reduce audio quality if needed |
| Voice cloning quality insufficient | Set user expectations; provide disclaimer; allow model swapping |
| Audio alignment drift over time | Implement timestamp validation; add manual adjustment tools if needed |
| Browser recording not supported | Provide fallback upload-only mode; document browser requirements |
| Export audio has artifacts | Improve cross-fading; add quality settings; test with different audio types |

### 6.2 MVP Scope Creep Prevention

If a task grows beyond MVP scope:
1. Document the expanded requirement
2. Propose deferring to post-MVP
3. Get explicit approval before implementing
4. Update requirements.md if scope officially changes

---

## 7. Definition of Done (Project-Level)

The MVP is complete when:
- [ ] All phases (0-10) are complete
- [ ] All tasks in TASKBOARD.md are marked "Done"
- [ ] All acceptance criteria met
- [ ] All FR (Functional Requirements) from requirements.md implemented
- [ ] All NFR (Non-Functional Requirements) verified
- [ ] Full user workflow can be completed without errors:
  - Upload 5-minute audio → Transcribe → Edit text → Delete words → Replace words → Adjust pauses → Play → Export
- [ ] Documentation complete (README, API docs, CONTRIBUTING)
- [ ] No critical bugs or blockers
- [ ] Human review and approval obtained

---

## 8. Post-MVP Roadmap (Out of Scope)

Future enhancements to consider after MVP:
- Multi-speaker diarization and separate track editing
- Multi-language support
- Video editing (audio sync with video timeline)
- Cloud storage and collaboration features
- Advanced audio effects (EQ, compression, noise reduction)
- Batch processing for multiple files
- Mobile app version
- Plugin architecture for custom models

---

## 9. Contact & Questions

For questions or clarifications on this workplan:
1. Refer to requirements.md for authoritative specifications
2. Consult AI.md for behavioral guidelines
3. Check AGENTS.md for coding conventions
4. Ask the human project owner for ambiguous requirements

---

## 10. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-15 | Initial comprehensive workplan created | AI Agent |

---

**Next Step:** Review this workplan, then proceed to TASKBOARD.md for detailed task tracking.
