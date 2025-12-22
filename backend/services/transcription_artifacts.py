from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from backend.models.project import Project
from backend.models.transcript import Transcript
from backend.services.transcript_refinement import refine_transcript
from backend.utils.storage import save_transcript, save_transcript_named
from backend.utils.timestamp_refinement_config import (
    METADATA_TRANSCRIPT_ACTIVE_SOURCE,
    METADATA_TRANSCRIPT_ASR_PATH,
    METADATA_TRANSCRIPT_ORIGINAL_PATH,
    METADATA_TRANSCRIPT_PATH,
    METADATA_TRANSCRIPT_REFINED_PATH,
    TRANSCRIPT_ASR_FILENAME,
    TRANSCRIPT_ORIGINAL_FILENAME,
    TRANSCRIPT_REFINED_FILENAME,
    TimestampRefinementConfig,
)

logger = logging.getLogger("textaudio")


@dataclass(frozen=True, slots=True)
class PersistedTranscriptArtifacts:
    transcript_path: str
    transcript_asr_path: str
    transcript_refined_path: str | None
    transcript_original_path: str
    transcript_active_source: str


def persist_transcription_artifacts(
    *,
    project: Project,
    audio_path: str,
    transcript_asr: Transcript,
    config: TimestampRefinementConfig,
) -> PersistedTranscriptArtifacts:
    """Persist ASR/refined/original/active transcripts and update project metadata.

    - `transcript_asr.json` always stores the raw STT output.
    - `transcript_refined.json` is written only when refinement is enabled and succeeds.
    - `transcript.json` is always written as the active transcript served to the UI.
    - `transcript_original.json` is written once as the immutable baseline for edit rebuilds.
    """

    asr_path = save_transcript_named(project.id, transcript_asr, TRANSCRIPT_ASR_FILENAME)

    refined: Transcript | None = None
    refined_path: str | None = None
    if config.enabled:
        try:
            refinement = refine_transcript(
                audio_path=audio_path, transcript_asr=transcript_asr, config=config
            )
            refined = refinement.refined
        except Exception as exc:  # noqa: BLE001
            logger.warning("Transcript refinement failed: %s", exc)
            refined = None

    if refined is not None:
        refined_path_obj = save_transcript_named(
            project.id, refined, TRANSCRIPT_REFINED_FILENAME
        )
        refined_path = str(refined_path_obj)

    active = refined if refined is not None else transcript_asr
    active_source = "refined" if refined is not None else "asr"
    active_path = save_transcript(project.id, active)

    original_path_raw = project.metadata.get(METADATA_TRANSCRIPT_ORIGINAL_PATH)
    if isinstance(original_path_raw, str):
        original_path = original_path_raw
        if not Path(original_path).exists():
            original_path_obj = save_transcript_named(
                project.id, active, Path(original_path).name
            )
            original_path = str(original_path_obj)
            project.metadata[METADATA_TRANSCRIPT_ORIGINAL_PATH] = original_path
    else:
        original_path_obj = save_transcript_named(
            project.id, active, TRANSCRIPT_ORIGINAL_FILENAME
        )
        original_path = str(original_path_obj)
        project.metadata[METADATA_TRANSCRIPT_ORIGINAL_PATH] = original_path

    project.metadata[METADATA_TRANSCRIPT_PATH] = str(active_path)
    project.metadata[METADATA_TRANSCRIPT_ASR_PATH] = str(asr_path)
    project.metadata[METADATA_TRANSCRIPT_ACTIVE_SOURCE] = active_source
    if refined_path is not None:
        project.metadata[METADATA_TRANSCRIPT_REFINED_PATH] = refined_path
    else:
        project.metadata.pop(METADATA_TRANSCRIPT_REFINED_PATH, None)

    return PersistedTranscriptArtifacts(
        transcript_path=str(active_path),
        transcript_asr_path=str(asr_path),
        transcript_refined_path=refined_path,
        transcript_original_path=original_path,
        transcript_active_source=active_source,
    )
