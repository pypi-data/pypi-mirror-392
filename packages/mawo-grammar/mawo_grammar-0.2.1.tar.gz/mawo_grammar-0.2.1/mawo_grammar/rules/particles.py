"""Particle usage rules for Russian grammar.

Validates usage of Russian particles: же, ли, бы, то, ка, таки, etc.
"""

from __future__ import annotations

from typing import Any

from ..errors import ErrorSeverity, GrammarError
from .base import Rule, RuleResult


class ParticleUsageRule(Rule):
    """Check particle usage in Russian.

    Russian particles:
    - же (emphasis, contrast): "Он же сказал!"
    - ли (question): "Знаешь ли ты?"
    - бы (conditional): "Я бы пошел"
    - то, ка, таки (various functions)
    """

    def __init__(self) -> None:
        """Initialize particle usage rule."""
        super().__init__(rule_id="PARTICLE_USAGE", category="particles", severity="minor")

        # Particles and their typical positions
        self.particles = {
            "же": "after_verb",  # Usually after verb
            "ли": "after_verb",  # Usually after verb in questions
            "бы": "after_verb",  # Usually after verb in conditional
            "то": "suffix",  # Usually as suffix (-то)
            "ка": "suffix",  # Usually as suffix (-ка)
            "таки": "suffix",  # Usually as suffix (-таки)
        }

    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check particle usage.

        Args:
            text: Text to check
            morphology: Optional MAWOMorphAnalyzer instance

        Returns:
            RuleResult with particle errors
        """
        errors: list[GrammarError] = []
        tokens = text.split()

        # Check for common particle mistakes
        for i, token in enumerate(tokens):
            token_lower = token.lower()

            # Check standalone particles that should be suffixes
            if token_lower in ("то", "ка", "таки"):
                # These should typically be attached with hyphen
                if i > 0:
                    prev_token = tokens[i - 1]

                    # Check if previous token is suitable for this particle
                    if token_lower == "то" and not prev_token.endswith("-"):
                        start = len(" ".join(tokens[: i - 1]))
                        if i > 1:
                            start += 1
                        end = start + len(prev_token) + 1 + len(token)

                        errors.append(
                            GrammarError(
                                type="particle_usage",
                                location=(start, end),
                                severity=ErrorSeverity.MINOR,
                                description=(
                                    f"Particle '{token_lower}' should be " f"attached with hyphen"
                                ),
                                suggestion=f"{prev_token}-{token_lower}",
                                rule_id=self.rule_id,
                                confidence=0.85,
                            )
                        )

            # Check for double particles (common mistake)
            if i < len(tokens) - 1:
                next_token = tokens[i + 1].lower()
                if token_lower in self.particles and next_token in self.particles:
                    start = len(" ".join(tokens[:i]))
                    if i > 0:
                        start += 1
                    end = start + len(token) + 1 + len(tokens[i + 1])

                    errors.append(
                        GrammarError(
                            type="particle_usage",
                            location=(start, end),
                            severity=ErrorSeverity.MAJOR,
                            description=(
                                f"Double particle usage: '{token_lower}' " f"and '{next_token}'"
                            ),
                            suggestion="Use only one particle",
                            rule_id=self.rule_id,
                            confidence=0.90,
                        )
                    )

        return RuleResult(errors=errors)
