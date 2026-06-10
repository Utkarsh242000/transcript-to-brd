from pathlib import Path

import pytest

from streamlit_app import convert_transcript_to_brd


def test_convert_transcript_to_brd_generates_docx(tmp_path: Path) -> None:
    transcript = tmp_path / "meeting.txt"
    transcript.write_text(
        "Product Owner: The objective is to simplify onboarding.\n"
        "BA: In scope includes KYC and profile setup.\n"
        "QA: Out of scope excludes legacy migration.",
        encoding="utf-8",
    )

    brd_bytes, filename, summary = convert_transcript_to_brd(
        upload_path=transcript,
        output_dir=tmp_path / "output",
    )

    assert filename == "meeting_brd.docx"
    assert brd_bytes.startswith(b"PK")
    assert summary["utterance_count"] > 0
    assert summary["chunk_count"] > 0


def test_convert_transcript_to_brd_rejects_empty_file(tmp_path: Path) -> None:
    transcript = tmp_path / "empty.txt"
    transcript.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        convert_transcript_to_brd(upload_path=transcript, output_dir=tmp_path / "output")
