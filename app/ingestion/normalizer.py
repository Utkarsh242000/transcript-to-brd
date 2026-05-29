"""
Text normalization and cleaning.
"""

import re
from typing import List
from app.utils.types import UtteranceSegment
from app.utils.helpers import clean_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TextNormalizer:
    """Normalize and clean transcript text."""

    # Markers for off-topic content
    OFF_TOPIC_MARKERS = [
        r"\[.*?off.topic.*?\]",
        r"\[.*?aside.*?\]",
        r"\[.*?joke.*?\]",
        r"\[.*?side.note.*?\]",
        r"\(.*?off.topic.*?\)",
    ]

    # Markers for system events
    SYSTEM_MARKERS = [
        r"\[.*?recording.*?\]",
        r"\[.*?screen.share.*?\]",
        r"\[.*?participant.*?joined.*?\]",
        r"\[.*?participant.*?left.*?\]",
        r"\[.*?call.ended.*?\]",
        r"\[.*?muted.*?\]",
        r"\[.*?unmuted.*?\]",
    ]

    @staticmethod
    def normalize_utterances(utterances: List[UtteranceSegment]) -> List[UtteranceSegment]:
        """
        Normalize list of utterances.

        Args:
            utterances: List of UtteranceSegment objects

        Returns:
            List of normalized utterances
        """
        logger.info(f"Normalizing {len(utterances)} utterances")
        normalized = []

        for utterance in utterances:
            normalized_text = TextNormalizer.normalize_text(utterance.text)

            # Skip empty utterances after normalization
            if not normalized_text:
                logger.debug(f"Skipping empty utterance from {utterance.speaker}")
                continue

            utterance.text = normalized_text
            normalized.append(utterance)

        logger.info(f"Retained {len(normalized)} utterances after normalization")
        return normalized

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize single text block.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Remove off-topic markers and content
        for marker in TextNormalizer.OFF_TOPIC_MARKERS:
            text = re.sub(marker, "", text, flags=re.IGNORECASE)

        # Remove system event markers
        for marker in TextNormalizer.SYSTEM_MARKERS:
            text = re.sub(marker, "", text, flags=re.IGNORECASE)

        # Clean text (remove fillers, normalize whitespace)
        text = clean_text(text)

        # Fix common transcription errors
        text = TextNormalizer._fix_transcription_errors(text)

        # Normalize quotes
        text = TextNormalizer._normalize_quotes(text)

        # Normalize contractions
        text = TextNormalizer._normalize_contractions(text)

        return text

    @staticmethod
    def _fix_transcription_errors(text: str) -> str:
        """Fix common transcription errors."""
        # Common OCR/speech-to-text errors
        replacements = {
            r"\bu\b": "you",
            r"\br\b": "are",
            r"\bw\/o\b": "without",
            r"\bw\/\b": "with",
            r"\b&\b": "and",
            r"\bthru\b": "through",
        }

        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def _normalize_quotes(text: str) -> str:
        """Normalize different quote styles."""
        # Convert smart quotes to straight quotes
        text = text.replace("\u201c", '"')
        text = text.replace("\u201d", '"')
        text = text.replace("\u2018", "'")
        text = text.replace("\u2019", "'")
        return text

    @staticmethod
    def _normalize_contractions(text: str) -> str:
        """Expand common contractions for better processing."""
        contractions = {
            r"\bcan't\b": "cannot",
            r"\bwon't\b": "will not",
            r"\bdon't\b": "do not",
            r"\bdoesn't\b": "does not",
            r"\bdidn't\b": "did not",
            r"\bshouldn't\b": "should not",
            r"\bwouldn't\b": "would not",
            r"\bcouldn't\b": "could not",
            r"\bisn't\b": "is not",
            r"\baren't\b": "are not",
            r"\bwasn't\b": "was not",
            r"\bweren't\b": "were not",
            r"\bhaven't\b": "have not",
            r"\bhasn't\b": "has not",
            r"\bhadn't\b": "had not",
        }

        for contraction, expansion in contractions.items():
            text = re.sub(contraction, expansion, text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def is_relevant_utterance(text: str) -> bool:
        """Check if utterance is relevant (not just noise)."""
        if not text or len(text) < 5:
            return False

        # Check for high concentration of numbers/symbols
        alphanumeric_ratio = sum(c.isalnum() for c in text) / len(text)
        if alphanumeric_ratio < 0.3:
            return False

        return True

    @staticmethod
    def get_utterance_quality_score(text: str) -> float:
        """
        Get quality score for utterance (0.0 to 1.0).

        Args:
            text: Utterance text

        Returns:
            Quality score
        """
        if not text:
            return 0.0

        score = 1.0

        # Penalize very short utterances
        if len(text) < 10:
            score -= 0.2

        # Penalize high concentration of numbers/symbols
        alphanumeric_ratio = sum(c.isalnum() for c in text) / len(text)
        if alphanumeric_ratio < 0.5:
            score -= 0.3

        # Penalize all uppercase (likely formatting noise)
        if text.isupper() and len(text) > 5:
            score -= 0.2

        return max(0.0, score)