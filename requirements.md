# requirements.md

## 1. Overview

**Product name (working):** TextAudio Edit (placeholder)  
**Type:** Local web/desktop app (front-end + local backend)  
**MVP focus:**  
> Let a single user upload or record a short audio clip (2–5 minutes), auto-generate a transcript, and then **edit the audio by editing text**, including **replacing words using an AI-generated voice** that matches the speaker.

All advanced/extra features are explicitly **out of scope** for the MVP (no multi-speaker, no teacher dashboards, no collaboration, no cloud SaaS).

The app is intended to run **locally on a single machine** (e.g., your laptop) with all audio and model processing happening locally where possible.

---

## 2. Goals & Non-Goals

### 2.1 Goals (MVP)

1. **Simple text-based audio editing**
   - User can edit audio by editing a transcript in a basic text editor UI.
   - Deleting text removes the corresponding audio.
   - Changing selected text triggers re-generation of that segment’s audio in the user’s voice.

2. **Automatic voice learning from short sample**
   - The system learns the user’s voice from the uploaded recording (no manual training workflow).
   - When the user edits words, new audio is generated in a voice that sounds like the original speaker (good enough for demos, not necessarily perfect studio quality).

3. **Minimal, intuitive UI**
   - Single-page experience:
     - Upload/Record
     - Transcribe
     - Edit + Play
     - Export
   - No audio waveform editing UI is required; transcript-centric editing is the primary interface.

4. **Local deployment**
   - All core functionality (upload, storage, transcription, editing, export, voice synthesis) is available **without needing a remote cloud backend**.
   - The app can run on a single machine using local models and/or locally hosted containers.

### 2.2 Non-Goals (MVP)

- Multi-user or collaborative editing.
- Teacher/coach features, rubrics, feedback tools.
- Multi-speaker diarisation and separate tracks.
- Video editing (audio-only MVP).
- Full-blown DAW features (mixing, EQ, effects).
- Production-grade SEO, authentication, marketing site, payment systems.
- Support for extremely long recordings (limit MVP to ~10 minutes max).

---

## 3. User & Use Case

### 3.1 User persona (MVP)

- Single user (e.g., a student) on their own machine.
- Technical level: can install apps / use a browser, but not a professional audio engineer.
- Primary use case:
  - They record themselves reading a 2–5 minute presentation script.
  - They realize there are mistakes, long pauses, or wording they want to change.
  - Instead of re-recording everything, they:
    1. Upload/record into the app.
    2. Let the app generate a transcript.
    3. Edit the text like a document.
    4. Export the corrected audio.

### 3.2 Key user stories

1. **Upload & transcribe**
   - As a user, I want to upload a short audio file and get a transcript so that I can edit my speech as text.
2. **Delete mistakes**
   - As a user, I want to delete words/sentences in the transcript so that the corresponding audio is removed.
3. **Fix a mis-spoken word**
   - As a user, I want to correct a word in the transcript and have the audio updated in my own voice without re-recording.
4. **Trim long pauses**
   - As a user, I want to reduce overly long pauses (silences) so that my recording sounds more natural.
5. **Playback from selection**
   - As a user, I want to click in the transcript and play from that point in the audio so I can quickly review changes.
6. **Export final audio**
   - As a user, I want to export the edited result as a single audio file (e.g., WAV/MP3) so that I can submit it or share it.

---

## 4. Functional Requirements

### 4.1 Project lifecycle

**FR-1**: The app shall support a simple “project” that consists of:
- Original audio file(s).
- Transcript with timestamped tokens/segments.
- Edit operations (deletions, replacements, pause adjustments).
- Generated audio segments for replacements.

**FR-2**: The user shall be able to:
- Create a new project by uploading an audio file.
- Optionally, record directly in the app for a new project.
- Save/load a project from disk (e.g., as a folder or `.json` + audio files).

*(If saving/loading feels too big for MVP, this can be deferred; but spec it here.)*

---

### 4.2 Audio input

**FR-3**: Supported input formats (minimum):
- WAV (16-bit PCM)
- MP3

**FR-4**: Duration constraints:
- MVP target: 2–5 minutes typical, hard limit ~10 minutes.
- If input exceeds hard limit, app should display a friendly error.

**FR-5**: Recording:
- The app shall allow recording from default microphone via browser (if web UI) or OS APIs.
- Recording is mono by default (simplify processing).
- Recording sample rate is normalized (e.g., 16kHz or 24kHz) for model compatibility.

---

### 4.3 Transcription

**FR-6**: For each uploaded/recorded audio:
- The backend shall perform automatic speech recognition (ASR) to produce a transcript.

**FR-7**: The transcript shall have **word-level or token-level timestamps**:
- `start_time` and `end_time` for each token or word.
- Sufficient resolution to allow reasonably precise audio alignment.

**FR-8**: The ASR should support at least English for MVP.

**FR-9**: After transcription completes:
- The full transcript is displayed in the text editor.
- Basic formatting: spaces, punctuation; no need for complex formatting (bold, bullets, etc.).

---

### 4.4 Text editor & selection model

**FR-10**: The main UI component is a **text editor** showing the transcript.
- User can click to place cursor.
- User can select words/sentences via mouse or keyboard.

**FR-11**: Each word in the editor is internally mapped to its corresponding time span in the audio.
- The mapping must be maintained through edits (insert/delete/replace), at least at the segment level.

**FR-12**: When the user selects a region of text, the app can:
- Play audio from the start of that region.
- Highlight the word currently being played (optional but highly desirable).

**FR-13**: Editor supports:
- Insert text.
- Delete text.
- Replace selected text with new text.
- Undo/redo of text edits.

---

### 4.5 Text-based deletion → audio editing

**FR-14**: When the user deletes a word or a range of words in the transcript:
- The corresponding audio segment(s) shall be marked as **removed**.

**FR-15**: For playback:
- The app shall skip removed segments, playing only the “kept” portions in sequence.

**FR-16**: For export:
- The backend shall render the final audio by concatenating:
  - Original audio segments that are kept.
  - Any AI-generated replacement segments.
  - With appropriate cross-fades at boundaries to avoid clicks/pops where feasible.

---

### 4.6 Pause detection and adjustment

**FR-17**: The backend shall detect **silence segments** beyond a configurable threshold (e.g., > 1.0 second).
- Silence is defined by low amplitude below a threshold for a continuous period.

**FR-18**: The user shall be able to:
- Select a silence region (e.g., represented in the transcript as a special token `[pause 2.3s]`) and
- Specify a new duration (e.g., 0.5s).

**FR-19**: The backend shall adjust the audio accordingly:
- Trimming or padding the silence audio segment to the new duration.

*(MVP implementation can be simple: only trimming long pauses, no complex time-stretching.)*

---

### 4.7 Voice learning and TTS replacement

**FR-20**: The system shall automatically extract a **speaker voice representation** from the input audio.
- No explicit “train voice” button needed; it happens once after upload/transcription.
- For MVP, assume **single speaker** only.

**FR-21**: When the user changes text in place (e.g., replace a word):
- The app shall:
  - Identify the associated original audio time span.
  - Generate a **replacement audio segment** using a voice model that approximates the user’s voice.
  - Align the timing to fit into that region as naturally as possible (within a tolerance).

**FR-22**: The generated replacement audio must:
- Use the previously learned voice embedding/profile.
- Follow the approximate prosody of the surrounding context (MVP: can be basic, not perfect).

**FR-23**: Each AI-generated segment is stored separately and tagged with:
- `start_time` in the logical timeline.
- Duration.
- Reference to text content.

**FR-24**: If the user edits the same region again:
- The system can re-generate and replace that segment.

---

### 4.8 Playback controls

**FR-25**: At minimum, the player shall support:
- Play / Pause
- Seeking by clicking in the transcript (play from clicked word/token).
- Display of current playback position (e.g., timecode and text highlight).

**FR-26**: Optional but desirable:
- Playback speed control (0.75x, 1x, 1.25x, 1.5x).
- Loop playback for selected text region.

---

### 4.9 Export

**FR-27**: The user shall be able to export:
- The final edited audio as a single file (e.g., WAV or MP3).
- The aligned transcript as a `.txt` or `.json` file (optional for MVP, but useful long term).

**FR-28**: Export operation runs on the backend:
- Combines original and generated segments.
- Applies simple normalization to avoid clipping.

---

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-1**: Target transcription time:
- For a 5-minute recording on a modern laptop, transcription should ideally complete within ~1–2 minutes (depending on chosen model and hardware).

**NFR-2**: Voice generation:
- Single-word or short-phrase replacement should complete in a few seconds for acceptable UX.

**NFR-3**: Export:
- Exporting a 5-minute audio should complete within ~1–2 minutes on the target machine.

---

### 5.2 Local deployment & offline friendliness

**NFR-4**: The app runs locally:
- Backend: local server (e.g., Python/Node) or desktop app.
- Frontend: local web UI or embedded browser (Electron-style), accessible at `http://localhost:PORT` or similar.

**NFR-5**: All audio and model data remain on the local machine by default.
- No automatic uploads to third-party servers.
- Any optional cloud integration in the future must be opt-in and clearly labelled.

---

### 5.3 Privacy & security

**NFR-6**: User audio files are stored only in specified local folders (e.g., within project directory).
**NFR-7**: No external telemetry or analytics in MVP.
**NFR-8**: Any logging must avoid storing raw audio or full transcriptions; logs should be minimal and local.

---

### 5.4 Usability

**NFR-9**: The UI should be understandable for a first-time user without a tutorial:
- Clear labels: “1. Upload or Record”, “2. Generate Transcript”, “3. Edit & Play”, “4. Export”.
- Avoid audio jargon (no “bus”, “aux send”, etc.).

**NFR-10**: Error messages should be plain language:
- e.g., “This file is too long (over 10 minutes). Please trim it and try again."

---

## 6. Architecture (High-Level)

### 6.1 Components

- **Frontend**
  - Single-page web UI (React/Vue/vanilla – implementation detail).
  - Responsible for:
    - File selection/recording UI.
    - Displaying transcript in a text editor.
    - Sending edit operations to backend.
    - Controlling playback (via HTML5 audio or custom audio player).

- **Backend**
  - REST or WebSocket API server running locally.
  - Responsible for:
    - Receiving and storing uploaded audio.
    - Running ASR (e.g., local Whisper or other ASR model).
    - Managing transcript + timestamp data structures.
    - Running voice embedding/voice cloning model.
    - Generating replacement audio segments.
    - Rendering/exporting final audio output.
    - Project persistence (optional for MVP).

- **Local storage**
  - File system directories for:
    - Raw audio.
    - Intermediate processed audio.
    - Project metadata (JSON).

### 6.2 Suggested data models (conceptual)

- `Project`
  - `id`
  - `created_at`, `updated_at`
  - `audio_original_path`
  - `transcript_tokens[]`: list of `{ id, text, start, end, type }` where `type` ∈ { word, punctuation, pause }
  - `edits[]` (optional operation log)

- `AudioSegment`
  - `id`
  - `source` ∈ { original, generated }
  - `source_file_path`
  - `logical_start_time`
  - `logical_end_time`
  - `linked_tokens[]` (ids of tokens covered)

---

## 7. Technical Constraints & Assumptions

- MVP targets **single-speaker English audio**.
- Processing may require a machine with at least:
  - Reasonable CPU (and optionally GPU for faster inference).
  - Enough disk space to store multiple versions of audio.
- Exact choice of ASR/TTS models is implementation-specific, but they must:
  - Run locally.
  - Support voice cloning from a relatively short sample.
- You may accept that **MVP voice quality is “good demo quality”**, not necessarily identical to the original voice.

---

## 8. Open Questions (for later)

- How will projects be persisted between sessions? (JSON spec, folder structure.)
- Should we support multi-language transcription in later versions?
- How to version control model configs and parameters?
- How to handle catastrophic edits (e.g., user deletes almost everything) – any auto backup/recovery?

