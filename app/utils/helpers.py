"""
Utility helper functions.
"""

import re
from typing import List, Optional
from datetime import datetime
import json


def clean_text(text: str) -> str:
    """
    Clean transcript text by removing filler words and extra whitespace.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove common filler words
    fillers = [
        r"\buh\b", r"\bum\b", r"\blike\b", r"\bso\b",
        r"\byou know\b", r"\bkind of\b", r"\bsort of\b",
        r"\breally\b", r"\bactually\b", r"\bbasically\b",
        r"\bliterally\b", r"\bonestly\b", r"\bI mean\b",
        r"\byeah\b", r"\byup\b", r"\bnope\b", r"\bmmhmm\b"
    ]

    for filler in fillers:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


def parse_timestamp(timestamp_str: str) -> Optional[float]:
    """
    Parse timestamp string to seconds.

    Supports formats:
    - "00:05:30" -> 330 seconds
    - "1:02:15" -> 3735 seconds
    - "45" -> 45 seconds
    - "45.5" -> 45.5 seconds

    Args:
        timestamp_str: Timestamp string

    Returns:
        Seconds as float, or None if parsing fails
    """
    timestamp_str = timestamp_str.strip()

    try:
        # Try HH:MM:SS format
        if ":" in timestamp_str:
            parts = timestamp_str.split(":")
            if len(parts) == 3:
                hours, minutes, seconds = map(float, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(float, parts)
                return minutes * 60 + seconds

        # Try plain seconds
        return float(timestamp_str)
    except ValueError:
        return None


def format_timestamp(seconds: float) -> str:
    """
    Format seconds to HH:MM:SS string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.findall(pattern, text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    return re.findall(pattern, text)


def extract_dates(text: str) -> List[str]:
    """
    Extract date-like patterns from text.

    Supports: MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD, etc.
    """
    patterns = [
        r"\d{1,2}/\d{1,2}/\d{2,4}",
        r"\d{1,2}-\d{1,2}-\d{2,4}",
        r"\d{4}-\d{1,2}-\d{1,2}",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
    ]
    results = []
    for pattern in patterns:
        results.extend(re.findall(pattern, text, re.IGNORECASE))
    return results


def extract_numbers(text: str) -> List[str]:
    """Extract numeric values from text."""
    pattern = r"\b\d+\.?\d*\b"
    return re.findall(pattern, text)


def is_speaker_change(prev_speaker: Optional[str], curr_speaker: Optional[str]) -> bool:
    """Check if there's a speaker change."""
    if prev_speaker is None or curr_speaker is None:
        return False
    return prev_speaker.strip().lower() != curr_speaker.strip().lower()


def get_uuid() -> str:
    """Generate a UUID string."""
    from uuid import uuid4
    return str(uuid4())


def save_json(data: dict, filepath: str) -> None:
    """Save data as JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> dict:
    """Load data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_dicts(*dicts) -> dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix