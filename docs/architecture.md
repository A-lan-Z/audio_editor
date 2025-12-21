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

## Transcript Editor & Mapping (Phase 4)

### Editor goals

- Render the transcript as a sequence of word “bubbles” (chip-style UI).
- Treat **words as the smallest editable unit**:
  - Backspace/delete removes a whole word (never half a word).
  - Typing creates an in-progress word; when committed (space / cursor move) it becomes a bubble.
- Maintain alignment back to the original ASR token IDs and timestamps for later audio editing.

### Data model

We represent the current editor document as an ordered list of nodes:

- `TokenNode` (original ASR word token)
  - `tokenId`: UUID (from `Transcript.tokens[].id`)
  - `text`: displayed text for the word
  - `start`, `end`: timestamps from the ASR token
  - `status`: `original | deleted | replaced`
- `InsertNode` (user-inserted word)
  - `id`: local UUID/string
  - `text`: inserted word text
  - `status`: `inserted`
  - No timestamps / no ASR token ID yet

Punctuation:
- We attach punctuation to the previous `TokenNode` for display, but treat word tokens as the primary selectable/editable units (selection/mapping returns word tokens).

### Mapping index (cursor/selection)

Even though the UI is word-based, the backend `EditOperation.position` is defined as a **character offset** in the current text. To support cursor/selection mapping efficiently:

- Compute `visibleText` by joining nodes with spaces using the same spacing rules as rendering.
- Build an index of spans:
  - For each word bubble, compute `[charStart, charEnd)` within `visibleText`
  - Store `tokenId` (for `TokenNode`) or `null` (for `InsertNode`)
- `position -> token` uses binary search over the spans (O(log n)).

Selections:
- Selection range is tracked in terms of word indices.
- Selected tokens are derived from the selected word indices (word tokens only).

### Edit operations

Operations are derived from UI interactions:

- `delete`: marks selected `TokenNode` as `deleted` (or deletes the previous word bubble if no explicit selection).
- `insert`: inserts an `InsertNode` at the current cursor index when a typed word is committed.
- `replace`: marks selected tokens as `replaced` and inserts one or more `InsertNode` words in their place.

Undo/redo:
- Frontend keeps undo/redo stacks and applies inverse transformations to the node list.
- Backend stores an append-only operation log for project state reconstruction.

