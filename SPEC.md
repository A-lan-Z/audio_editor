# AI Audio Editor — Product Spec

## Vision

A web-based audio editor where teams record separately and the app makes it sound like they were in the same room. Users edit audio by editing text in a collaborative, script-style interface — with AI handling audio normalization, seamless transitions, pace matching, and filler word removal.

### Origin Story

Born from a university team project where members recorded a video presentation separately. The result: everyone's audio sounded wildly different — different volumes, different echo, different pace — and re-recording to fix mistakes made it even worse. The core insight: **people shouldn't have to be audio engineers just to combine recordings from different people and environments.**

### Core Problems Solved

1. **Multi-speaker audio mismatch** — different mics, rooms, and recording conditions produce jarring audio when combined. The app normalizes all speakers to a consistent studio standard.
2. **Re-recording sounds obvious** — when you re-record a segment, the new audio doesn't match the original. AI style transfer makes re-recordings blend seamlessly.
3. **Pace inconsistency** — different speakers talk at different speeds with different gap patterns. AI-assisted pace controls create natural, consistent flow.
4. **Audio editing is too technical** — the app lets you edit audio by editing a transcript, like editing a Google Doc.

---

## Target Users

- **Student/work teams** — recording presentations, demos, video voiceovers where each person records their part separately
- **Podcasters** — multi-host shows where hosts record remotely in different environments
- **Content creators** — preparing audio for YouTube, courses, social media
- **General users** — anyone combining audio from multiple sources or speakers

## Competitive Positioning

Simpler and cheaper than Adobe Audition. More audio control and better multi-speaker support than Descript. Higher quality than free online tools. The differentiator is **multi-speaker audio normalization** and the collaborative text-based editing workflow.

---

## MVP Features (V1)

### 1. Multi-File Upload & Ingest
- **Multiple input methods**:
  - **Direct upload**: one user creates a project and uploads everyone's audio files, assigning speaker names
  - **Shared project link**: creator shares a link; each team member uploads their own recording directly, creating their speaker profile automatically
  - **Merged file + diarization**: upload a single file (e.g., a call recording) and AI separates speakers automatically
- Accept any common audio format (MP3, WAV, M4A, FLAC, OGG, WEBM) via FFmpeg WASM conversion on upload
- Convert to a normalized internal format (WAV) for processing
- Support files from short clips (<10 min) to long recordings (1-3 hours) with adaptive loading:
  - Short files: load entirely into browser memory
  - Medium/long files: chunked loading, server-side processing, client loads visible chunks on demand
- Export as **MP3** or **WAV** only

### 2. Transcription & Speaker Identification
- Server-side transcription using OpenAI Whisper (or equivalent)
- Word-level timestamps for precise audio-text mapping
- **Speaker labels**: each transcribed segment is tagged with the speaker's name
  - For separate file uploads: speaker is known from the file/uploader
  - For merged files: speaker diarization assigns speaker IDs, user maps them to names
- Click-to-listen: clicking any word in the transcript plays that specific audio segment so users can verify accuracy
- Users can freely correct transcription errors in the text editor

### 3. Script-Style Text Editing
- **Transcript-primary UI**: the transcript is the main editing surface; waveform is secondary/collapsible
- **Script-style layout**: like a screenplay — each block shows `SPEAKER NAME: text`, making it clear who said what
- Supported operations:
  - **Delete** words, sentences, or selections
  - **Reorder** segments via drag-and-drop or cut/paste
  - **Trim** — select a range in the transcript to keep, discard the rest
- **Immediate preview, explicit commit**: playback reflects edits in real-time (non-destructive segment stitching), but the final audio file is only rendered on export
- Full undo/redo history

### 4. Audio Normalization to Studio Standard
- All speakers' audio is normalized to a clean, consistent "studio standard" sound regardless of original recording quality
- **Per-speaker controls**: each speaker gets individual normalization settings so users can fine-tune:
  - Volume / loudness
  - EQ / frequency response
  - Noise floor / background noise removal
  - Reverb / room echo removal
  - Compression / dynamics
- Normalization is applied non-destructively; original audio is preserved

### 5. AI-Smoothed Transitions
- **This is the paramount focus of V1** — text-based edits must produce audio that is indistinguishable from the original unedited recording
- When a user deletes or reorders segments, the AI smooths the audio at edit boundaries
- Uses AI to regenerate short boundary audio for natural-sounding transitions (not just crossfade)
- Voice profile is auto-cloned from each speaker's uploaded audio
- **Legal safeguard**: consent checkbox confirming the user has rights to all voices in the audio

### 6. Export
- Render the edited, normalized audio to MP3 or WAV
- All speakers' audio is normalized and blended into a single cohesive output
- Server-side rendering for long files; client-side for short clips where feasible

---

## V2 Features (Post-MVP)

### Audio Generation & Insertion
- **Short corrections (1-3 words)**: auto-generate via TTS using the speaker's cloned voice model
- **Longer additions**: prompt the user to record the new segment, then:
  - Use AI style transfer to match the new recording to the project's studio standard
  - The new recording seamlessly blends with the rest of the audio
- Free tier gets limited audio generation credits; paid unlocks full usage

### Pace Editing
- **Gap adjustment**: control silence/gaps between sentences, between speakers, and between words
- **AI pace suggestions**: AI analyzes all speakers and suggests optimal gap durations for natural conversational flow
- Users can accept AI suggestions or manually fine-tune gaps
- Speech speed adjustment per speaker (careful, natural-sounding time-stretching)

### Filler Word Removal
- AI auto-detects filler words ("um", "uh", "like", "you know", "so", etc.)
- Filler words are highlighted in the transcript
- One-click removal of all fillers, or selective removal per instance
- AI-smoothed transitions at removal points

### Real-Time Collaboration
- **Google Docs-style collaboration**: multiple team members can view and edit the transcript simultaneously
- Real-time cursor presence (see where others are editing)
- Conflict resolution for simultaneous edits (CRDT-based)
- Yjs or Automerge for CRDT-based editing, WebSocket provider for sync

### Additional V2 Features
- AI auto-ordering: if a script exists, AI suggests the arrangement of speaker segments to match the script
- Multi-track export (separate files per speaker)
- Video sync — align edited audio back to a video timeline
- Template projects (e.g., "team presentation", "podcast episode", "video voiceover")

---

## Architecture

### Frontend
- **Framework**: Choose based on best fit — React is recommended for ecosystem size and library availability
- **Audio engine**: Use **wavesurfer.js** for waveform rendering and **Tone.js** or the Web Audio API (via a wrapper library) for real-time segment playback/stitching
- **FFmpeg WASM** for client-side format conversion on upload
- **Text editor**: Rich text editor (e.g., TipTap or ProseMirror) adapted for script-style transcript with speaker labels and word-level audio mappings

### Backend
- **Python (FastAPI)** — best ecosystem for AI/audio processing:
  - Whisper integration for transcription
  - Speaker diarization (pyannote.audio or similar)
  - librosa / torchaudio for audio analysis, normalization, and processing
  - PyTorch for AI model inference (voice cloning, boundary smoothing, style transfer in V2)
- **Job queue** (e.g., Celery + Redis, or a managed queue) for async AI processing tasks
- **File storage**: S3-compatible object storage for uploaded and processed audio files
- **Database**: PostgreSQL for project metadata, user accounts, speaker profiles

### Hybrid Processing Model
- **Client-side (browser)**:
  - Format conversion (FFmpeg WASM)
  - Waveform rendering
  - Real-time playback of edited segments (non-destructive stitching)
  - Short file export
- **Server-side**:
  - Transcription (Whisper)
  - Speaker diarization
  - Audio normalization to studio standard
  - AI boundary smoothing
  - Voice cloning / profile generation per speaker
  - Long file export rendering
  - V2: style transfer, TTS generation, collaboration WebSocket relay

### Deployment
- **Frontend**: Vercel
- **Backend API + WebSocket**: Railway (or similar managed platform)
- **AI workers**: Railway or a GPU-enabled service (e.g., Modal, Replicate, RunPod) for model inference
- **Database**: Railway managed PostgreSQL or Supabase
- Minimize operational complexity — managed services wherever possible for solo development

---

## Data Model (Conceptual)

```
Project
├── speakers[]
│   ├── name
│   ├── original_audio_file (immutable, stored in object storage)
│   ├── voice_profile (auto-generated from their audio)
│   └── normalization_settings (per-speaker EQ, volume, noise, reverb, compression)
├── transcript
│   └── segments[]
│       ├── speaker_id
│       ├── words[] (word, start_time, end_time, confidence, is_filler)
│       └── source_file_ref
├── edit_state (current arrangement of segments — the "playlist")
├── edit_history[] (undo/redo stack)
└── exports[] (rendered output files)
```

The edit state is a non-destructive playlist of segment references into the original audio files. Playback reconstructs audio from this playlist. Export renders it to a final file with all normalization and AI processing applied.

---

## Monetization

### Freemium Model
- **Free tier**:
  - Upload, transcribe, text-edit, export (core loop)
  - Basic audio normalization
  - Basic crossfade transitions
  - Limited audio generation credits (V2)
- **Paid tier**:
  - AI-smoothed transitions
  - Advanced per-speaker normalization controls
  - AI pace suggestions (V2)
  - Unlimited collaborators (V2)
  - Unlimited audio generation (V2)
  - Longer file support
  - Priority processing queue

---

## Key Technical Risks

| Risk | Mitigation |
|------|-----------|
| Studio standard normalization quality varies wildly with input quality | Provide per-speaker manual controls as escape hatch; set realistic expectations for very poor input audio |
| Speaker diarization accuracy (for merged file uploads) | Use pyannote.audio (state-of-the-art); let users manually correct speaker assignments; support separate file upload as the primary path |
| AI boundary smoothing quality may not be good enough | Start with high-quality crossfade as fallback; iterate on AI model quality. Users can toggle between AI and simple crossfade |
| Whisper transcription errors degrade the editing experience | Click-to-listen verification; easy inline correction |
| Real-time segment stitching in the browser is complex | Use established libraries (wavesurfer.js, Tone.js); pre-buffer adjacent segments for gapless playback |
| Long file handling adds significant architectural complexity | Start with a 60-min file limit for V1; extend with chunked streaming architecture later |
| Voice cloning legal/ethical exposure | Consent checkbox; clear ToS; no storage of voice profiles beyond the project lifetime |
| Solo developer operational burden | Managed services only (Vercel, Railway); no self-managed infrastructure; use third-party APIs where possible |
| GPU compute costs for AI inference | Feature-gate expensive operations behind paid tier; use batching and caching; consider Replicate/Modal pay-per-use pricing |

---

## Recommended MVP Build Order

### V1 Build Order
1. **Project scaffold** — frontend + backend skeleton, file upload, object storage, user auth
2. **Multi-speaker upload** — support multiple file uploads per project with speaker assignment
3. **Transcription pipeline** — upload → Whisper → word-level transcript with speaker labels displayed in script-style UI
4. **Transcript editor** — script-style text editing with click-to-listen, delete, reorder, drag-and-drop
5. **Audio normalization** — per-speaker studio standard normalization with individual controls
6. **Playback engine** — non-destructive real-time playback from edit state (multi-speaker segment stitching)
7. **AI transitions** — AI-smoothed boundary audio generation (the core differentiator — iterate until edits are undetectable)
8. **Basic export** — render normalized, edited audio to MP3/WAV
9. **Polish** — undo/redo, error handling, loading states, onboarding UX

### V2 Build Order
10. **Filler word removal** — auto-detect and highlight fillers, one-click removal with AI-smoothed transitions
11. **Pace editing** — gap adjustment with AI-suggested durations
12. **Real-time collaboration** — Yjs/CRDT integration, WebSocket sync, cursor presence
13. **Shared upload links** — team members upload their own recordings via a shared project link
14. **Speaker diarization** — support merged file upload with auto speaker separation
15. **Audio generation** — TTS for short corrections, style transfer for re-recordings
