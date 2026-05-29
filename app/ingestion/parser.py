"""
Parse speaker turns and timestamps from transcript.
"""

import re
from typing import List, Optional, Tuple
from app.utils.types import UtteranceSegment
from app.utils.helpers import parse_timestamp
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TranscriptParser:
    """Parse speaker turns, timestamps, and utterances."""

    # Common speaker patterns
    SPEAKER_PATTERNS = [
        r"^(\w+(?:\s+\w+)?)\s*[:\-]\s*(.+)",  # "John Smith: text" or "John Smith - text"
        r"^\[(\w+(?:\s+\w+)?)\]\s*(.+)",      # "[John Smith] text"
        r"^(\w+(?:\s+\w+)?)\s+(?:says?|said|noted|mentioned|replied):\s*(.+)",
    ]

    # Common timestamp patterns
    TIMESTAMP_PATTERNS = [
        r"(?:\[|\()(\d{1,2}:\d{2}(?::\d{2})?)\s*(?:\]|\))",  # [HH:MM:SS] or (HH:MM:SS)
        r"<(\d{1,2}:\d{2}(?::\d{2})?)>",                       # <HH:MM:SS>
    ]

    @staticmethod
    def parse_utterances(text: str, infer_speakers: bool = True) -> List[UtteranceSegment]:
        """
        Parse transcript into utterance segments.

        Args:
            text: Raw transcript text
            infer_speakers: If True, infer speakers from speaker patterns

        Returns:
            List of UtteranceSegment objects
        """
        logger.info("Parsing transcript into utterances")
        utterances = []
        lines = text.split("\n")

        current_speaker: Optional[str] = None
        current_text_lines: List[str] = []
        current_timestamp: Optional[float] = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to extract timestamp
            timestamp = TranscriptParser._extract_timestamp(line)
            if timestamp is not None:
                current_timestamp = timestamp
                # Remove timestamp from line for processing
                line = TranscriptParser._remove_timestamps(line)
                if not line:
                    continue

            # Try to extract speaker
            speaker_match = TranscriptParser._match_speaker(line)
            if speaker_match:
                # Save previous utterance if any
                if current_text_lines:
                    utterances.append(
                        UtteranceSegment(
                            speaker=current_speaker or "Unknown",
                            text=" ".join(current_text_lines),
                            timestamp_start=current_timestamp,
                        )
                    )
                    current_text_lines = []

                current_speaker, line_text = speaker_match
                current_text_lines.append(line_text)
            else:
                # Continuation of previous speaker
                current_text_lines.append(line)

        # Save last utterance
        if current_text_lines:
            utterances.append(
                UtteranceSegment(
                    speaker=current_speaker or "Unknown",
                    text=" ".join(current_text_lines),
                    timestamp_start=current_timestamp,
                )
            )

        logger.info(f"Parsed {len(utterances)} utterances")
        return utterances

    @staticmethod
    def _extract_timestamp(line: str) -> Optional[float]:
        """Extract timestamp from line."""
        for pattern in TranscriptParser.TIMESTAMP_PATTERNS:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                return parse_timestamp(timestamp_str)
        return None

    @staticmethod
    def _remove_timestamps(line: str) -> str:
        """Remove timestamp markers from line."""
        for pattern in TranscriptParser.TIMESTAMP_PATTERNS:
            line = re.sub(pattern, "", line)
        return line.strip()

    @staticmethod
    def _match_speaker(line: str) -> Optional[Tuple[str, str]]:
        """
        Try to match speaker pattern.

        Returns:
            Tuple of (speaker_name, remaining_text) or None
        """
        for pattern in TranscriptParser.SPEAKER_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                speaker = match.group(1).strip()
                text = match.group(2).strip()
                return (speaker, text)
        return None

    @staticmethod
    def extract_speaker_list(utterances: List[UtteranceSegment]) -> List[str]:
        """Extract unique speaker list."""
        speakers = []
        seen = set()
        for utterance in utterances:
            if utterance.speaker and utterance.speaker not in seen:
                speakers.append(utterance.speaker)
                seen.add(utterance.speaker)
        return speakers

    @staticmethod
    def calculate_utterance_duration(utterances: List[UtteranceSegment]) -> Optional[float]:
        """Calculate total transcript duration."""
        if not utterances:
            return None

        # Find min and max timestamps
        timestamps = [u.timestamp_start for u in utterances if u.timestamp_start]
        if not timestamps:
            return None

        return max(timestamps) - min(timestamps)