# Timestamp Refinement Pipeline (Phase 3.5)

This document defines the Phase 3.5 “best approach” pipeline for transcript-driven editing accuracy:

1) (Optional) **Top-tier STT** for best transcript text and initial word timestamps  
2) (Optional) **Forced alignment** to refine word start/end times against the chosen transcript text  
3) **Boundary snapping + padding** to make cut boundaries robust for delete/replace operations  
4) Persist **artifacts** and expose **diagnostics** so correctness is observable

The goal is to prevent failures like “deleted content still audible” and to preserve natural pauses without reintroducing speech.

## Inputs / Outputs

**Inputs**
- `audio_path`: normalized project audio (mono WAV)
- `transcript_asr`: tokens with initial word timestamps (from local ASR or optional online STT)

**Outputs**
- `transcript_refined`: same token text/IDs, improved `start/end` boundaries
- `refinement_diagnostics`: per-token boundary adjustments (before/after + reason)

## Artifact files (project directory)

The project should store multiple transcript artifacts for reproducibility:
- `transcript_original.json`: immutable snapshot used as the base for edit rebuilds
- `transcript_asr.json`: raw STT output (local or online provider)
- `transcript_refined.json`: refined timestamps (if refinement enabled and succeeds)
- `transcript.json`: the **active** transcript served to the frontend

## Project metadata pointers

To keep downstream code stable and enable switching sources:
- `metadata.transcript_path`: path to the **active** transcript (served by `GET /transcript`)
- `metadata.transcript_asr_path`: path to `transcript_asr.json`
- `metadata.transcript_refined_path`: path to `transcript_refined.json` (if available)
- `metadata.transcript_active_source`: one of `asr` | `refined`

## Configuration knobs (env vars)

These are read at runtime and should never be committed with user secrets:

- `TEXTAUDIO_REFINE_TIMESTAMPS` (`0/1`, default `0`): enable refinement stage
- `TEXTAUDIO_ALIGNMENT_BACKEND` (default `none`): `none` | `mfa` | other (pluggable)
- `TEXTAUDIO_SNAP_MODE` (default `rms`): `rms` | `vad` (pluggable)
- `TEXTAUDIO_SNAP_WINDOW_MS` (default `200`): search window around a boundary
- `TEXTAUDIO_CUT_PADDING_MS` (default `40`): padding applied to delete/replace cuts

Provider config for optional online STT is defined in `T359` and remains opt-in.

## How this interacts with later phases

- **Phase 4 (Editor):** token IDs and token text must remain stable across refinement so edit logs referencing `old_tokens` remain valid.
- **Phase 5 (Deletion → Audio):** segments should be initialized from the active/refined transcript boundaries to reduce speech leakage at cut boundaries.
- **Phase 8 (Playback):** diagnostics should help validate click-to-play and highlight accuracy.
- **Phase 9 (Export):** export should use the same active/refined boundaries as preview to avoid mismatch.

