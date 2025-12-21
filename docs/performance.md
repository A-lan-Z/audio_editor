# Performance Notes

## Transcription (Phase 3 / NFR-1)

Goal: transcription of a 5-minute clip should ideally complete in ~1–2 minutes on a modern laptop (hardware-dependent).

### Benchmark script

Run a quick local benchmark using synthetic audio (no real user data):

```bash
.venv/bin/python scripts/benchmark_transcription.py --model tiny --seconds 300
```

Optional profiling:

```bash
.venv/bin/python scripts/benchmark_transcription.py --model tiny --seconds 300 --profile
```

Notes:
- The script generates a synthetic WAV file under `./models/` (gitignored) if needed.
- Synthetic audio is used to keep the repo free of user audio and to make runs deterministic; real speech accuracy/performance should be validated locally with user-provided audio.

### Optimization levers

- Model size: `tiny` (fastest) → `base` → `small` (better accuracy, slower).
- Compute type: CPU `int8` is the default in this repo for speed and lower memory usage.
- Model caching: first run includes model init/download; subsequent runs should reuse the cache in `./models/` (or `TEXTAUDIO_MODELS_DIR`).

### Current benchmark (synthetic)

On this repo environment (CPU, model `tiny`, warm run, synthetic 5-minute WAV):
- ~1.84s for 5 minutes of audio (`warm_seconds_per_minute≈0.37s`)

Profiling notes (cProfile, warm run):
- Most time is spent inside the ASR inference/token generation path (`generate_with_fallback`) and CTranslate2 encode/align calls.
