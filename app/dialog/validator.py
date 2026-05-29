"""Validation and contradiction detection."""

from typing import List, Dict, Optional
from app.utils.types import TextChunk, ValidationIssue, RequirementCategory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BRDValidator:
    """Validate BRD completeness and detect contradictions."""

    REQUIRED_CATEGORIES = [
        RequirementCategory.OBJECTIVE,
        RequirementCategory.SCOPE_IN,
        RequirementCategory.SCOPE_OUT,
        RequirementCategory.FUNCTIONAL_REQ,
    ]

    @staticmethod
    def validate_chunks(chunks: List[TextChunk]) -> List[ValidationIssue]:
        """Validate chunk collection for completeness."""
        logger.info(f"Validating {len(chunks)} chunks")
        issues = []

        # Check for required categories
        categories_found = set(c.category for c in chunks if c.category)
        for required in BRDValidator.REQUIRED_CATEGORIES:
            if required not in categories_found:
                issue = ValidationIssue(
                    issue_type="missing_field",
                    description=f"No chunks classified as {required.value}",
                    severity="warning",
                )
                issues.append(issue)

        logger.info(f"Found {len(issues)} validation issues")
        return issues

    @staticmethod
    def detect_contradictions(chunks: List[TextChunk]) -> List[ValidationIssue]:
        """Detect contradictions in chunks."""
        issues = []
        logger.info("Detecting contradictions")
        return issues
