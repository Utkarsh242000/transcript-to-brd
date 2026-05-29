"""BRD schema and data models."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from app.utils.types import FunctionalRequirement, NonFunctionalRequirement


@dataclass
class BRD:
    """Complete Business Requirement Document."""
    title: str
    document_id: str
    version: str = "1.0"
    executive_summary: str = ""
    business_objectives: List[str] = field(default_factory=list)
    scope_in: List[str] = field(default_factory=list)
    scope_out: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    functional_requirements: List[FunctionalRequirement] = field(default_factory=list)
    nonfunctional_requirements: List[NonFunctionalRequirement] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "document_id": self.document_id,
            "version": self.version,
            "business_objectives": self.business_objectives,
            "scope_in": self.scope_in,
            "scope_out": self.scope_out,
        }
