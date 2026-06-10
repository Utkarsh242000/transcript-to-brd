"""Streamlit web app for transcript-to-BRD conversion."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import streamlit as st

from app.brd.composer import BRDComposer
from app.config import get_config
from app.export.docx_exporter import DOCXExporter
from app.ingestion.loader import TranscriptLoader
from app.ingestion.normalizer import TextNormalizer
from app.ingestion.parser import TranscriptParser
from app.utils.logger import get_logger
from app.utils.types import RequirementCategory, TextChunk

SUPPORTED_UPLOAD_TYPES = ["txt", "vtt", "docx"]
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_MAX_EXECUTIVE_SUMMARY_CHARS = 700
_MAX_EXECUTIVE_SUMMARY_UTTERANCES = 3
_MAX_SECTION_ITEMS = 10
_TIMESTAMP_FORMAT_UTC = "%Y%m%d%H%M%S"
logger = get_logger(__name__)


def _classify_text(text: str) -> RequirementCategory:
    lower = text.lower()

    if any(phrase in lower for phrase in ["out of scope", "exclude", "excluded", "not in scope"]):
        return RequirementCategory.SCOPE_OUT
    if any(phrase in lower for phrase in ["in scope", "include", "included", "within scope"]):
        return RequirementCategory.SCOPE_IN
    if any(word in lower for word in ["objective", "goal", "aim", "purpose"]):
        return RequirementCategory.OBJECTIVE
    if any(word in lower for word in ["acceptance criteria", "done when", "success criteria"]):
        return RequirementCategory.ACCEPTANCE_CRITERIA
    if any(word in lower for word in ["risk", "concern", "issue", "blocker"]):
        return RequirementCategory.RISK

    return RequirementCategory.FUNCTIONAL_REQ


def _build_chunks_from_utterances(utterances: list) -> list[TextChunk]:
    chunks: list[TextChunk] = []

    for idx, utterance in enumerate(utterances):
        text = utterance.text.strip()
        if not TextNormalizer.is_relevant_utterance(text):
            continue

        chunks.append(
            TextChunk(
                text=text,
                chunk_index=len(chunks),
                total_chunks=0,
                source_segment_ids=[utterance.id],
                category=_classify_text(text),
                confidence=1.0,
                metadata={"speaker": utterance.speaker, "source_index": idx},
            )
        )

    total = len(chunks)
    for chunk in chunks:
        chunk.total_chunks = total

    return chunks


def convert_transcript_to_brd(upload_path: Path, output_dir: Path) -> tuple[bytes, str, dict[str, Any]]:
    """Convert a transcript file to BRD bytes using existing app modules."""
    get_config()  # Validates and initializes app configuration directories.

    transcript_text = TranscriptLoader.load(upload_path)
    if not transcript_text.strip():
        raise ValueError("The uploaded transcript is empty.")

    utterances = TranscriptParser.parse_utterances(transcript_text)
    normalized_utterances = TextNormalizer.normalize_utterances(utterances)
    if not normalized_utterances:
        raise ValueError("No usable transcript content found after normalization.")

    chunks = _build_chunks_from_utterances(normalized_utterances)
    if not chunks:
        raise ValueError("No relevant transcript statements were found for BRD generation.")

    timestamp = datetime.now(timezone.utc).strftime(_TIMESTAMP_FORMAT_UTC)
    document_id = f"BRD-{timestamp}"
    title = f"Business Requirement Document - {upload_path.stem}"

    brd = BRDComposer.compose(title=title, document_id=document_id, chunks=chunks)
    brd.executive_summary = " ".join(
        u.text for u in normalized_utterances[:_MAX_EXECUTIVE_SUMMARY_UTTERANCES]
    )[
        :_MAX_EXECUTIVE_SUMMARY_CHARS
    ]
    brd.risks = [c.text for c in chunks if c.category == RequirementCategory.RISK][
        :_MAX_SECTION_ITEMS
    ]
    brd.acceptance_criteria = [
        c.text for c in chunks if c.category == RequirementCategory.ACCEPTANCE_CRITERIA
    ][:_MAX_SECTION_ITEMS]

    fallback_objective = (
        normalized_utterances[0].text
        if normalized_utterances
        else "Requirements captured from uploaded transcript."
    )
    if not brd.business_objectives:
        brd.business_objectives = [fallback_objective]

    output_dir.mkdir(parents=True, exist_ok=True)
    output_filename = f"{upload_path.stem}_brd.docx"
    output_path = output_dir / output_filename
    DOCXExporter.export(brd, output_path)

    return output_path.read_bytes(), output_filename, {
        "utterance_count": len(normalized_utterances),
        "chunk_count": len(chunks),
    }


def _reset_download_state() -> None:
    for key in ("brd_bytes", "brd_filename", "conversion_summary", "uploaded_name"):
        st.session_state.pop(key, None)


def main() -> None:
    st.set_page_config(
        page_title="Transcript to BRD Converter",
        page_icon="📝",
        layout="centered",
    )

    st.title("📝 Transcript to BRD Converter")
    st.caption("Upload a transcript, convert it, and download a BRD `.docx` in one flow.")

    uploaded_file = st.file_uploader(
        "Upload transcript",
        type=SUPPORTED_UPLOAD_TYPES,
        help="Supported formats: .txt, .vtt, .docx",
    )

    if uploaded_file is None:
        _reset_download_state()
    elif st.session_state.get("uploaded_name") != uploaded_file.name:
        _reset_download_state()
        st.session_state["uploaded_name"] = uploaded_file.name

    convert_clicked = st.button(
        "Convert transcript to BRD",
        type="primary",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

    if convert_clicked:
        if uploaded_file is None:
            st.error("Please upload a transcript file before converting.")
            st.stop()

        try:
            file_name = Path(uploaded_file.name).name
            suffix = Path(file_name).suffix.lower().lstrip(".")
            if suffix not in SUPPORTED_UPLOAD_TYPES:
                raise ValueError(
                    f"Unsupported file format: .{suffix}. Supported formats are: "
                    + ", ".join(f".{ext}" for ext in SUPPORTED_UPLOAD_TYPES)
                )

            with TemporaryDirectory(prefix="transcript_to_brd_") as temp_dir:
                temp_path = Path(temp_dir) / file_name
                temp_path.write_bytes(uploaded_file.getbuffer())

                with st.spinner("Converting transcript to BRD..."):
                    brd_bytes, brd_filename, summary = convert_transcript_to_brd(
                        upload_path=temp_path,
                        output_dir=Path(temp_dir) / "output",
                    )

            st.session_state["brd_bytes"] = brd_bytes
            st.session_state["brd_filename"] = brd_filename
            st.session_state["conversion_summary"] = summary
            st.success("Conversion completed successfully.")

        except (ValueError, FileNotFoundError) as exc:
            st.error(f"Conversion failed: {exc}")
        except Exception as exc:  # pragma: no cover - defensive error handling
            logger.exception("Unexpected error during transcript conversion")
            st.error(f"Unexpected error during conversion: {exc}")

    if st.session_state.get("brd_bytes"):
        summary = st.session_state.get("conversion_summary") or {}
        if summary:
            st.info(
                f"Processed **{summary.get('utterance_count', 0)}** utterances into "
                f"**{summary.get('chunk_count', 0)}** BRD chunks."
            )

        st.download_button(
            label="Download BRD (.docx)",
            data=st.session_state["brd_bytes"],
            file_name=st.session_state.get("brd_filename", "generated_brd.docx"),
            mime=_DOCX_MIME,
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
