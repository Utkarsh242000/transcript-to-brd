"""
Transcript file loader supporting .txt, .vtt, and .docx formats.
"""

from pathlib import Path
from typing import Optional, List
from app.utils.types import UtteranceSegment
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TranscriptLoader:
    """Load transcripts from various file formats."""

    @staticmethod
    def load(file_path: Path) -> str:
        """
        Load transcript from file.

        Args:
            file_path: Path to transcript file (.txt, .vtt, or .docx)

        Returns:
            Raw transcript text

        Raises:
            ValueError: If file format not supported
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Transcript file not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            return TranscriptLoader._load_txt(file_path)
        elif suffix == ".vtt":
            return TranscriptLoader._load_vtt(file_path)
        elif suffix == ".docx":
            return TranscriptLoader._load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    @staticmethod
    def _load_txt(file_path: Path) -> str:
        """Load from plain text file."""
        logger.info(f"Loading transcript from .txt: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"Successfully loaded {len(content)} characters from .txt")
            return content
        except Exception as e:
            logger.error(f"Error loading .txt file: {e}")
            raise

    @staticmethod
    def _load_vtt(file_path: Path) -> str:
        """Load from WebVTT file, extracting text without timestamps."""
        logger.info(f"Loading transcript from .vtt: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            text_lines = []
            for line in lines:
                line = line.strip()
                # Skip VTT header
                if line.startswith("WEBVTT"):
                    continue
                # Skip timestamps (HH:MM:SS.mmm --> HH:MM:SS.mmm)
                if "-->" in line:
                    continue
                # Skip empty lines and metadata
                if line and not line.startswith("NOTE"):
                    text_lines.append(line)

            content = "\n".join(text_lines)
            logger.info(f"Successfully loaded {len(content)} characters from .vtt")
            return content
        except Exception as e:
            logger.error(f"Error loading .vtt file: {e}")
            raise

    @staticmethod
    def _load_docx(file_path: Path) -> str:
        """Load from .docx file."""
        logger.info(f"Loading transcript from .docx: {file_path}")
        try:
            from docx import Document
            doc = Document(file_path)
            text_lines = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_lines.append(para.text)
            content = "\n".join(text_lines)
            logger.info(f"Successfully loaded {len(content)} characters from .docx")
            return content
        except ImportError:
            logger.error("python-docx not installed. Install with: pip install python-docx")
            raise
        except Exception as e:
            logger.error(f"Error loading .docx file: {e}")
            raise