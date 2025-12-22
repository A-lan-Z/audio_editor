import numpy as np
import soundfile as sf

from backend.api.diagnostics import get_timestamp_diagnostics
from backend.models.project import Project
from backend.models.transcript import Token, Transcript
from backend.utils.storage import project_original_wav_path, save_project_metadata


def test_timestamp_diagnostics_returns_token_timings_and_boundary_trims(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_REFINE_TIMESTAMPS", "1")
    monkeypatch.setenv("TEXTAUDIO_SNAP_WINDOW_MS", "0")
    monkeypatch.setenv("TEXTAUDIO_CUT_PADDING_MS", "0")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 1_000
    audio = np.zeros((sample_rate,), dtype=np.float32)
    sf.write(audio_path, audio, sample_rate, subtype="PCM_16")

    token_a = Token(text="one", start=0.0, end=0.25, type="word")
    token_b = Token(text="two", start=0.5, end=0.75, type="word")

    asr = Transcript(tokens=[token_a, token_b], language="en", duration=0.75)
    refined = Transcript(
        tokens=[
            token_a.model_copy(update={"start": 0.01, "end": 0.24}),
            token_b.model_copy(update={"start": 0.51, "end": 0.74}),
        ],
        language="en",
        duration=0.75,
    )

    project_dir = audio_path.parent
    transcript_asr_path = project_dir / "transcript_asr.json"
    transcript_refined_path = project_dir / "transcript_refined.json"
    transcript_path = project_dir / "transcript.json"
    transcript_asr_path.write_text(asr.to_json(), encoding="utf-8")
    transcript_refined_path.write_text(refined.to_json(), encoding="utf-8")
    transcript_path.write_text(refined.to_json(), encoding="utf-8")

    project.metadata["transcript_path"] = str(transcript_path)
    project.metadata["transcript_asr_path"] = str(transcript_asr_path)
    project.metadata["transcript_refined_path"] = str(transcript_refined_path)
    project.metadata["transcript_active_source"] = "refined"
    project.metadata["segments"] = [
        {
            "id": str(token_a.id),
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.25,
            "status": "kept",
            "token_ids": [str(token_a.id)],
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.25,
            "end": 0.5,
            "status": "removed",
            "token_ids": [],
        },
        {
            "id": str(token_b.id),
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.5,
            "end": 0.75,
            "status": "kept",
            "token_ids": [str(token_b.id)],
        },
    ]
    save_project_metadata(project)

    response = get_timestamp_diagnostics(project.id)
    assert response.project_id == project.id
    assert response.transcript_active_source == "refined"
    assert response.refinement_enabled is True
    assert len(response.tokens) == 2
    rows = {str(row.id): row for row in response.tokens}
    assert rows[str(token_a.id)].asr_start == 0.0
    assert rows[str(token_a.id)].refined_start == 0.01
    assert response.boundary_trims[0].prev_segment_id == token_a.id
    assert response.boundary_trims[0].next_segment_id == token_b.id
