"""Audit trail recording."""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuditTrail:
    """Record audit trail for all actions."""

    def __init__(self, output_dir: Path):
        """Initialize audit trail."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events: List[Dict[str, Any]] = []

    def record(
        self,
        action: str,
        entity: str,
        entity_id: str,
        details: Dict[str, Any],
        performed_by: str = "system",
    ) -> None:
        """Record an event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "entity": entity,
            "entity_id": entity_id,
            "performed_by": performed_by,
            "details": details,
        }
        self.events.append(event)
        logger.info(f"Audit: {action} on {entity} {entity_id}")

    def save(self, filename: str = "audit_trail.json") -> Path:
        """Save audit trail to file."""
        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            json.dump(self.events, f, indent=2)
        logger.info(f"Audit trail saved to {output_path}")
        return output_path
