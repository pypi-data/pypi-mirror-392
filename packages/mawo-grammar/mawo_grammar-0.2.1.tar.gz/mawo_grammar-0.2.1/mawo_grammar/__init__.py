"""Russian grammar checker with 500+ rules.

This package provides comprehensive Russian grammar checking with:
- Case agreement validation
- Verb aspect checking
- Particle usage rules
- Preposition + case validation
- Register consistency checking

Example:
    >>> from mawo_grammar import RussianGrammarChecker
    >>> checker = RussianGrammarChecker()
    >>> errors = checker.check("красивая дом")
    >>> print(errors[0].description)
    'Adjective-noun gender mismatch: красивая (fem) + дом (masc)'
"""

from __future__ import annotations

from .checker import RussianGrammarChecker
from .errors import ErrorSeverity, GrammarError
from .rules.base import Rule, RuleResult

__version__ = "0.2.0"

__all__ = [
    "RussianGrammarChecker",
    "GrammarError",
    "ErrorSeverity",
    "Rule",
    "RuleResult",
]
