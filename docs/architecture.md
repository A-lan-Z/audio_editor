# Architecture Notes (MVP)

This doc captures implementation decisions that affect multiple phases.

## Transcription (Phase 3)

### Requirements recap

- Local-first ASR (no cloud dependency by default).
- Word/token-level timestamps (`start_time`, `end_time`) to support transcript-driven editing.
- Target performance: ~1–2 minutes to transcribe a 5-minute clip on a modern laptop (hardware-dependent).

### Options considered

#### faster-whisper (Whisper via CTranslate2)
- Pros:
  - Local-first, widely used Whisper implementation with good CPU performance.
  - Supports word-level timestamps for tokens/words when enabled.
  - Model files can be cached locally and reused across runs.
- Cons:
  - First run may require model download (handled in T304), which is large for bigger models.
  - Accuracy/performance trade-offs depend on model size and hardware.

#### openai-whisper (reference Whisper implementation)
- Pros:
  - Well-known baseline implementation.
- Cons:
  - Generally slower on CPU than optimized runtimes.
  - Word-level timestamps support is less straightforward and varies by approach.

#### Vosk (Kaldi-based)
- Pros:
  - Local-first, lighter-weight models.
- Cons:
  - Timestamp granularity/quality and transcript quality can vary; not the default path for this MVP.

### Decision

**Selected ASR engine for MVP: `faster-whisper`**

Rationale:
- Matches local-first constraints.
- Provides word-level timestamps needed for transcript-to-audio alignment.
- Gives a practical path to meeting `NFR-1` on CPU by choosing an appropriate model size.

### Local verification notes

Verified in this repo environment:
- `faster-whisper` runs locally on CPU and returns word timestamps when `word_timestamps=True`.
- Minimal sanity run (CPU, `compute_type=int8`, model `tiny`) produced segments with per-word `start/end`.

Initial performance estimate (CPU, model `tiny`, warm run):
- ~0.55s to transcribe ~20s of audio-like signal ⇒ ~1.7s per minute of audio (excludes first-load/download).

Notes:
- Real speech accuracy/timing quality must be validated with real speech audio (not committed to repo).
- Larger models (`base`, `small`) are expected to be slower but more accurate; we will tune defaults in T313.

