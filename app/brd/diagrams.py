"""Diagram generation utilities."""

from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DiagramGenerator:
    """Generate workflow and architecture diagrams."""

    @staticmethod
    def generate_workflow_diagram(output_path: Path) -> Path:
        """Generate workflow diagram."""
        logger.info("Generating workflow diagram")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
