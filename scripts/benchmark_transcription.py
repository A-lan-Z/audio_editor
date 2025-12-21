from __future__ import annotations

import argparse
import cProfile
import io
import os
import pstats
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.services.whisper_service import (  # noqa: E402
    WhisperConfig,
    WhisperTranscriptionService,
)


def _generate_synthetic_wav(
    path: Path, *, seconds: float, sample_rate_hz: int = 16_000
) -> None:
    samples = int(sample_rate_hz * seconds)
    rng = np.random.default_rng(0)
    audio = rng.integers(-2000, 2000, samples, dtype=np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, sample_rate_hz, subtype="PCM_16")


def _run_transcription(service: WhisperTranscriptionService, audio_path: Path) -> float:
    start = time.perf_counter()
    transcript = service.transcribe(str(audio_path))
    elapsed = time.perf_counter() - start
    print(
        f"tokens={len(transcript.tokens)} "
        f"duration_s={transcript.duration:.2f} "
        f"elapsed_s={elapsed:.3f}"
    )
    return elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark local ASR transcription")
    parser.add_argument(
        "--model", default="tiny", help="ASR model name (e.g. tiny/base/small)"
    )
    parser.add_argument(
        "--seconds", type=float, default=300.0, help="Synthetic audio duration"
    )
    parser.add_argument("--models-dir", default="models", help="Model cache directory")
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Run cProfile and print top hotspots",
    )
    args = parser.parse_args()

    os.environ["TEXTAUDIO_MODELS_DIR"] = args.models_dir

    audio_path = Path(args.models_dir) / f"_benchmark_{int(args.seconds)}s.wav"
    if not audio_path.exists():
        print(f"Generating synthetic audio: {audio_path} ({args.seconds}s)")
        _generate_synthetic_wav(audio_path, seconds=args.seconds)

    service = WhisperTranscriptionService(config=WhisperConfig(model_name=args.model))

    print("Cold run (includes any first-use initialization):")
    cold = _run_transcription(service, audio_path)

    print("Warm run:")
    warm = _run_transcription(service, audio_path)

    per_min = warm / max(args.seconds / 60.0, 1e-9)
    print(f"warm_seconds_per_minute={per_min:.3f}")

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()
        _run_transcription(service, audio_path)
        profiler.disable()

        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("tottime")
        stats.print_stats(25)
        print("\nTop cProfile hotspots:\n")
        print(stream.getvalue())

    _ = cold
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
