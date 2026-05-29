"""BRD assembly from processed chunks."""

from typing import List
from app.utils.types import TextChunk, FunctionalRequirement, RequirementCategory, MoSCoWPriority
from app.brd import BRD
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BRDComposer:
    """Assemble BRD from chunks and validated content."""

    @staticmethod
    def compose(title: str, document_id: str, chunks: List[TextChunk], confirmed_decisions: dict = None) -> BRD:
        """Compose BRD from chunks."""
        logger.info("Composing BRD from chunks")
        brd = BRD(title=title, document_id=document_id)
        
        # Extract objectives
        objectives = [c.text for c in chunks if c.category == RequirementCategory.OBJECTIVE]
        brd.business_objectives = objectives
        
        # Extract scope
        scope_in = [c.text for c in chunks if c.category == RequirementCategory.SCOPE_IN]
        scope_out = [c.text for c in chunks if c.category == RequirementCategory.SCOPE_OUT]
        brd.scope_in = scope_in
        brd.scope_out = scope_out
        
        logger.info("BRD composition complete")
        return brd
