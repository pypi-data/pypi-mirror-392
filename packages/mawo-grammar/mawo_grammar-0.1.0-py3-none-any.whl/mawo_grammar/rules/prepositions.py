"""Preposition + case rules for Russian grammar.

Validates correct case usage after prepositions.
"""

from __future__ import annotations

from typing import Any

from ..errors import ErrorSeverity, GrammarError
from .base import Rule, RuleResult


class PrepositionCaseRule(Rule):
    """Check preposition + case agreement in Russian.

    Russian prepositions require specific cases:
    - в/на + Accusative (motion): "в город", "на работу"
    - в/на + Prepositional (location): "в городе", "на работе"
    - с + Genitive: "с другом"
    - к + Dative: "к другу"
    - etc.
    """

    def __init__(self) -> None:
        """Initialize preposition + case rule."""
        super().__init__(rule_id="PREPOSITION_CASE", category="prepositions", severity="major")

        # Prepositions and their required cases
        self.preposition_cases = {
            # Genitive
            "без": ["gent"],
            "для": ["gent"],
            "до": ["gent"],
            "из": ["gent"],
            "от": ["gent"],
            "у": ["gent"],
            "с": ["gent", "accs", "ins"],  # Multiple cases possible
            # Dative
            "к": ["datv"],
            "по": ["datv", "accs"],  # Multiple cases
            # Accusative
            "про": ["accs"],
            "через": ["accs"],
            "в": ["accs", "loct"],  # в + acc (motion) or loc (location)
            "на": ["accs", "loct"],  # на + acc (motion) or loc (location)
            "за": ["accs", "ins"],
            "под": ["accs", "ins"],
            # Instrumental
            "над": ["ins"],
            "перед": ["ins"],
            "между": ["ins"],
            # Prepositional
            "о": ["loct"],
            "об": ["loct"],
            "при": ["loct"],
        }

    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check preposition + case usage.

        Args:
            text: Text to check
            morphology: Optional MAWOMorphAnalyzer instance

        Returns:
            RuleResult with preposition errors
        """
        if morphology is None:
            return RuleResult(errors=[])

        errors: list[GrammarError] = []
        tokens = text.split()

        if not hasattr(morphology, "parse"):
            return RuleResult(errors=[])

        for i in range(len(tokens) - 1):
            prep_token = tokens[i].lower()
            noun_token = tokens[i + 1]

            # Check if this is a known preposition
            if prep_token not in self.preposition_cases:
                continue

            # Parse the following noun
            noun_parses = morphology.parse(noun_token)
            if not noun_parses:
                continue

            noun_parse = noun_parses[0]
            if not hasattr(noun_parse, "tag"):
                continue

            noun_tag = noun_parse.tag

            # Check if it's a noun
            if not hasattr(noun_tag, "POS") or noun_tag.POS not in ("NOUN", "NPRO", "ADJF"):
                continue

            # Get actual case
            actual_case = getattr(noun_tag, "case", None)
            if actual_case is None:
                continue

            # Get required cases for this preposition
            required_cases = self.preposition_cases[prep_token]

            # Check if actual case is in required cases
            if actual_case not in required_cases:
                start = len(" ".join(tokens[:i]))
                if i > 0:
                    start += 1
                end = start + len(prep_token) + 1 + len(noun_token)

                # Try to suggest correction
                suggestion = None
                if len(required_cases) == 1 and hasattr(noun_parse, "inflect"):
                    # Inflect to required case
                    required_case = required_cases[0]
                    inflected = noun_parse.inflect({required_case})
                    if inflected and hasattr(inflected, "word"):
                        suggestion = f"{prep_token} {inflected.word}"

                # Build description
                if len(required_cases) == 1:
                    case_desc = required_cases[0]
                else:
                    case_desc = " or ".join(required_cases)

                errors.append(
                    GrammarError(
                        type="preposition_case",
                        location=(start, end),
                        severity=ErrorSeverity.MAJOR,
                        description=(
                            f"Preposition '{prep_token}' requires {case_desc}, "
                            f"got {actual_case}"
                        ),
                        suggestion=suggestion,
                        rule_id=self.rule_id,
                        confidence=0.95,
                        morphology={
                            "preposition": prep_token,
                            "required_cases": required_cases,
                            "actual_case": actual_case,
                            "noun": noun_token,
                        },
                    )
                )

        return RuleResult(errors=errors)
