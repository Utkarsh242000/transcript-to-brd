"""Question generation for clarification loop."""

from typing import List
from app.utils.types import ValidationIssue, ClarificationQuestion
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ClarificationGenerator:
    """Generate clarification questions from validation issues."""

    @staticmethod
    def generate_questions(issues: List[ValidationIssue]) -> List[ClarificationQuestion]:
        """Generate questions from issues."""
        logger.info(f"Generating questions from {len(issues)} issues")
        questions = []

        for issue in issues:
            if issue.resolved:
                continue

            question_text = f"Can you clarify: {issue.description}?"
            question = ClarificationQuestion(
                question=question_text,
                issue_ids=[issue.id],
                context=issue.description,
            )
            questions.append(question)

        logger.info(f"Generated {len(questions)} questions")
        return questions
