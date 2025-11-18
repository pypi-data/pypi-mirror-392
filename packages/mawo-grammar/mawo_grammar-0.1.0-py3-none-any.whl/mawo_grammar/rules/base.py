"""Base classes for grammar rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mawo_grammar.errors import GrammarError


@dataclass
class RuleResult:
    """Result of applying a grammar rule.

    Attributes:
        errors: List of detected grammar errors
        metadata: Optional metadata about the check
    """

    errors: list[GrammarError]
    metadata: dict[str, Any] | None = None


class Rule(ABC):
    """Base class for grammar rules.

    Each rule implements a specific grammar check (e.g., case agreement,
    aspect usage, etc.).
    """

    def __init__(self, rule_id: str, category: str, severity: str = "major") -> None:
        """Initialize rule.

        Args:
            rule_id: Unique identifier for this rule
            category: Rule category (e.g., 'agreement', 'aspect')
            severity: Default severity level
        """
        self.rule_id = rule_id
        self.category = category
        self.severity = severity

    @abstractmethod
    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check text for grammar errors.

        Args:
            text: Text to check
            morphology: Optional morphological analysis (from pymorphy3)

        Returns:
            RuleResult with detected errors
        """
        pass

    def enabled(self) -> bool:
        """Check if rule is enabled.

        Returns:
            True if rule should be applied
        """
        return True

    def __repr__(self) -> str:
        """String representation."""
        return f"<Rule {self.rule_id} ({self.category})>"
