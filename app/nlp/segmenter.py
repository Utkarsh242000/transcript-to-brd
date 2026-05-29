"""Topic-based segmentation."""

import re
from typing import List, Optional
from app.utils.types import UtteranceSegment
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TranscriptSegmenter:
    """Segment transcript into topic blocks."""

    TOPIC_KEYWORDS = {
        "objective": ["objective", "goal", "aim", "purpose"],
        "scope": ["scope", "include", "exclude"],
        "requirements": ["require", "requirement", "must"],
        "timeline": ["timeline", "deadline"],
        "risks": ["risk", "concern", "issue"],
    }

    @staticmethod
    def segment_utterances(utterances: List[UtteranceSegment]) -> List[List[UtteranceSegment]]:
        """Segment utterances into topic blocks."""
        logger.info(f"Segmenting {len(utterances)} utterances")
        if not utterances:
            return []
        return [utterances]