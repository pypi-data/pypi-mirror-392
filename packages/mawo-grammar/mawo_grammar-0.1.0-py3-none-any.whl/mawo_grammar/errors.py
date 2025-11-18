"""Grammar error definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    CRITICAL = "critical"  # Breaks grammatical structure
    MAJOR = "major"  # Clear grammatical error
    MINOR = "minor"  # Stylistic or optional


@dataclass
class GrammarError:
    """Represents a grammar error with rich context.

    Attributes:
        type: Error type (e.g., 'case_agreement', 'aspect_usage')
        location: Character span (start, end) in text
        severity: Error severity level
        description: Human-readable description
        suggestion: Corrected version
        rule_id: ID of the rule that detected this error
        confidence: Confidence score (0.0-1.0)
        morphology: Optional morphological context
    """

    type: str
    location: tuple[int, int]
    severity: ErrorSeverity
    description: str
    suggestion: str | None = None
    rule_id: str | None = None
    confidence: float = 1.0
    morphology: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate error fields."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1], got {self.confidence}")

        start, end = self.location
        if start < 0 or end < start:
            raise ValueError(f"Invalid location: {self.location}")

    def verify(self, text: str) -> bool:
        """Verify that error location is valid in text.

        Args:
            text: The text to verify against

        Returns:
            True if location is valid, False otherwise
        """
        start, end = self.location
        return 0 <= start < end <= len(text)

    def get_text_span(self, text: str) -> str:
        """Extract the text span corresponding to this error.

        Args:
            text: The full text

        Returns:
            Text substring at error location
        """
        start, end = self.location
        return text[start:end]

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "type": self.type,
            "location": list(self.location),
            "severity": self.severity.value,
            "description": self.description,
            "suggestion": self.suggestion,
            "rule_id": self.rule_id,
            "confidence": self.confidence,
            "morphology": self.morphology,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrammarError:
        """Create error from dictionary.

        Args:
            data: Dictionary with error data

        Returns:
            GrammarError instance
        """
        return cls(
            type=data["type"],
            location=tuple(data["location"]),
            severity=ErrorSeverity(data["severity"]),
            description=data["description"],
            suggestion=data.get("suggestion"),
            rule_id=data.get("rule_id"),
            confidence=data.get("confidence", 1.0),
            morphology=data.get("morphology"),
        )
