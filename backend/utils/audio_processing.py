from __future__ import annotations

from pathlib import Path

import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from backend.utils.errors import InvalidAudioFormat

SUPPORTED_EXTENSIONS: set[str] = {".wav", ".mp3"}


def validate_extension(path: Path) -> str:
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise InvalidAudioFormat(f"Unsupported file type: {ext or '(none)'}")
    return ext


def validate_audio_decodable(path: Path) -> None:
    ext = validate_extension(path)
    try:
        if ext == ".wav":
            with sf.SoundFile(path) as _:
                pass
        elif ext == ".mp3":
            AudioSegment.from_file(path)
        librosa.get_duration(path=str(path))
    except CouldntDecodeError as exc:
        raise InvalidAudioFormat(
            "Failed to decode audio. MP3 support may require ffmpeg to be installed."
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise InvalidAudioFormat("Failed to decode audio file") from exc


def convert_mp3_to_wav_pcm16(src_path: Path, dest_path: Path) -> None:
    try:
        segment = AudioSegment.from_file(src_path)
    except CouldntDecodeError as exc:
        raise InvalidAudioFormat(
            "Failed to decode MP3. Install ffmpeg and try again."
        ) from exc

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    segment.export(dest_path, format="wav")

    audio, sample_rate = sf.read(dest_path, dtype="float32", always_2d=False)
    sf.write(dest_path, audio, sample_rate, subtype="PCM_16")


def ensure_wav_pcm16(path: Path) -> Path:
    ext = validate_extension(path)
    if ext == ".wav":
        return path

    dest_path = path.with_suffix(".wav")
    convert_mp3_to_wav_pcm16(path, dest_path)
    return dest_path
