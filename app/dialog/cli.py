"""CLI interaction loop for clarifications."""

from typing import Optional, List
from app.utils.types import ClarificationQuestion
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CLIInteractor:
    """Handle interactive CLI dialog with user."""

    @staticmethod
    def ask_question(question: ClarificationQuestion) -> str:
        """Ask user a clarification question."""
        logger.info(f"Asking: {question.question}")
        print(f"\n{question.question}")
        return input("Your answer: ").strip()

    @staticmethod
    def ask_batch(questions: List[ClarificationQuestion]) -> dict:
        """Ask batch of questions."""
        answers = {}
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}]")
            answer = CLIInteractor.ask_question(question)
            answers[question.id] = answer
            question.answered = True
            question.answer = answer
        return answers

    @staticmethod
    def confirm(message: str) -> bool:
        """Ask for yes/no confirmation."""
        response = input(f"{message} (y/n): ").strip().lower()
        return response in ("y", "yes")
