"""
Type definitions and data models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import uuid4


class RequirementCategory(str, Enum):
    """Categories for requirement classification."""
    OBJECTIVE = "objective"
    SCOPE_IN = "scope_in"
    SCOPE_OUT = "scope_out"
    FUNCTIONAL_REQ = "functional_req"
    NONFUNCTIONAL_REQ = "nonfunctional_req"
    BUSINESS_RULE = "business_rule"
    DATA_RETENTION = "data_retention"
    SECURITY = "security"
    INTEGRATION = "integration"
    RISK = "risk"
    OPEN_QUESTION = "open_question"
    ASSUMPTION = "assumption"
    DEPENDENCY = "dependency"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    NOISE = "noise"


class MoSCoWPriority(str, Enum):
    """MoSCoW prioritization."""
    MUST = "MUST"
    SHOULD = "SHOULD"
    COULD = "COULD"
    WONT = "WONT"


@dataclass
class UtteranceSegment:
    """Represents a single speaker's utterance."""
    id: str = field(default_factory=lambda: str(uuid4()))
    speaker: str = ""
    timestamp_start: Optional[float] = None  # Seconds
    timestamp_end: Optional[float] = None    # Seconds
    text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def duration(self) -> Optional[float]:
        """Get duration in seconds."""
        if self.timestamp_start and self.timestamp_end:
            return self.timestamp_end - self.timestamp_start
        return None


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    id: str = field(default_factory=lambda: str(uuid4()))
    text: str = ""
    chunk_index: int = 0
    total_chunks: int = 0
    source_segment_ids: List[str] = field(default_factory=list)
    category: Optional[RequirementCategory] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_relevant(self, threshold: float = 0.5) -> bool:
        """Check if chunk is relevant based on confidence and category."""
        return self.category != RequirementCategory.NOISE and self.confidence >= threshold


@dataclass
class VectorRecord:
    """Record for vector store."""
    chunk_id: str
    vector: List[float]
    metadata: Dict[str, Any]


@dataclass
class ConfirmedFact:
    """Represents a fact confirmed by user or high-confidence extraction."""
    id: str = field(default_factory=lambda: str(uuid4()))
    fact: str = ""
    category: RequirementCategory = RequirementCategory.OBJECTIVE
    evidence_chunk_ids: List[str] = field(default_factory=list)
    user_confirmed: bool = False
    confirmed_by: Optional[str] = None
    confirmed_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1


@dataclass
class ValidationIssue:
    """Issue detected during validation."""
    id: str = field(default_factory=lambda: str(uuid4()))
    issue_type: str = ""  # "missing_field", "contradiction", "duplicate", etc.
    description: str = ""
    severity: str = "warning"  # "error", "warning", "info"
    evidence_chunk_ids: List[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class ClarificationQuestion:
    """A question for user clarification."""
    id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    issue_ids: List[str] = field(default_factory=list)
    options: List[str] = field(default_factory=list)
    context: Optional[str] = None
    answered: bool = False
    answer: Optional[str] = None
    answered_by: Optional[str] = None
    answered_at: Optional[datetime] = None


@dataclass
class FunctionalRequirement:
    """Functional requirement for BRD."""
    id: str = ""
    title: str = ""
    description: str = ""
    details: Optional[str] = None
    business_rules: List[str] = field(default_factory=list)
    priority: MoSCoWPriority = MoSCoWPriority.SHOULD
    owner: Optional[str] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    evidence_chunk_ids: List[str] = field(default_factory=list)


@dataclass
class NonFunctionalRequirement:
    """Non-functional requirement for BRD."""
    id: str = ""
    category: str = ""  # security, performance, availability, usability, etc.
    requirement: str = ""
    metrics: Optional[str] = None
    priority: MoSCoWPriority = MoSCoWPriority.SHOULD
    evidence_chunk_ids: List[str] = field(default_factory=list)


@dataclass
class BRDStatement:
    """Single statement in BRD with provenance."""
    id: str = field(default_factory=lambda: str(uuid4()))
    section: str = ""
    content: str = ""
    provenance: Dict[str, List[str]] = field(default_factory=dict)  # {source_type: [ids]}


@dataclass
class AuditRecord:
    """Audit trail record."""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    action: str = ""  # "created", "updated", "confirmed", "resolved", etc.
    entity_type: str = ""  # "requirement", "fact", "question", etc.
    entity_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    performed_by: Optional[str] = None
    transcript_id: Optional[str] = None


@dataclass
class ProcessingResult:
    """Result of transcript processing."""
    transcript_id: str
    utterances: List[UtteranceSegment]
    chunks: List[TextChunk]
    validation_issues: List[ValidationIssue]
    clarification_questions: List[ClarificationQuestion]
    functional_requirements: List[FunctionalRequirement]
    nonfunctional_requirements: List[NonFunctionalRequirement]
    audit_records: List[AuditRecord]
    metadata: Dict[str, Any] = field(default_factory=dict)