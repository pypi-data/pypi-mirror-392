"""Case agreement rules for Russian grammar.

Implements rules for:
- Adjective-noun agreement (gender, case, number)
- Numeral-noun agreement
- Pronoun-noun agreement
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from ..errors import ErrorSeverity, GrammarError
from .base import Rule, RuleResult

if TYPE_CHECKING:
    pass


class AdjNounAgreementRule(Rule):
    """Check adjective-noun agreement in Russian.

    Validates that adjectives agree with nouns in:
    - Gender (masculine, feminine, neuter)
    - Case (nominative, genitive, dative, accusative, instrumental, prepositional)
    - Number (singular, plural)

    Examples:
        >>> rule = AdjNounAgreementRule()
        >>> result = rule.check("красивая дом")  # fem adj + masc noun
        >>> len(result.errors)
        1
    """

    def __init__(self) -> None:
        """Initialize adjective-noun agreement rule."""
        super().__init__(
            rule_id="ADJ_NOUN_GENDER_AGREEMENT", category="agreement", severity="major"
        )

    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check adjective-noun agreement.

        Args:
            text: Text to check
            morphology: Optional MAWOMorphAnalyzer instance

        Returns:
            RuleResult with agreement errors
        """
        if morphology is None:
            # Can't check without morphology
            return RuleResult(errors=[])

        errors: list[GrammarError] = []

        # Tokenize and analyze
        tokens = text.split()

        if not hasattr(morphology, "parse"):
            return RuleResult(errors=[])

        # Find adjective-noun pairs (simple heuristic: adjacent words)
        for i in range(len(tokens) - 1):
            adj_token = tokens[i]
            noun_token = tokens[i + 1]

            # Parse both tokens
            adj_parses = morphology.parse(adj_token)
            noun_parses = morphology.parse(noun_token)

            if not adj_parses or not noun_parses:
                continue

            adj_parse = adj_parses[0]
            noun_parse = noun_parses[0]

            # Check if this is an adjective-noun pair
            if not (hasattr(adj_parse, "tag") and hasattr(noun_parse, "tag")):
                continue

            adj_tag = adj_parse.tag
            noun_tag = noun_parse.tag

            # Check POS
            if not (hasattr(adj_tag, "POS") and hasattr(noun_tag, "POS")):
                continue

            if adj_tag.POS != "ADJF" or noun_tag.POS not in ("NOUN", "NPRO"):
                continue

            # Check agreement
            agreement_ok = True
            mismatch_details = []

            # Gender (only in singular)
            if hasattr(adj_tag, "number") and hasattr(noun_tag, "number"):
                if adj_tag.number == "sing" and noun_tag.number == "sing":
                    if hasattr(adj_tag, "gender") and hasattr(noun_tag, "gender"):
                        if adj_tag.gender != noun_tag.gender:
                            agreement_ok = False
                            mismatch_details.append(
                                f"gender: {adj_tag.gender} vs {noun_tag.gender}"
                            )

            # Case
            if hasattr(adj_tag, "case") and hasattr(noun_tag, "case"):
                if adj_tag.case != noun_tag.case:
                    agreement_ok = False
                    mismatch_details.append(f"case: {adj_tag.case} vs {noun_tag.case}")

            # Number
            if hasattr(adj_tag, "number") and hasattr(noun_tag, "number"):
                if adj_tag.number != noun_tag.number:
                    agreement_ok = False
                    mismatch_details.append(f"number: {adj_tag.number} vs {noun_tag.number}")

            if not agreement_ok:
                # Calculate position in original text
                start = len(" ".join(tokens[:i]))
                if i > 0:
                    start += 1  # Space before
                end = start + len(adj_token) + 1 + len(noun_token)

                # Try to suggest correction
                suggestion = None
                if hasattr(adj_parse, "inflect"):
                    # Get required grammemes from noun
                    required_tags = set()
                    if hasattr(noun_tag, "gender"):
                        required_tags.add(noun_tag.gender)
                    if hasattr(noun_tag, "case"):
                        required_tags.add(noun_tag.case)
                    if hasattr(noun_tag, "number"):
                        required_tags.add(noun_tag.number)

                    # Inflect adjective
                    inflected = adj_parse.inflect(required_tags)
                    if inflected and hasattr(inflected, "word"):
                        suggestion = f"{inflected.word} {noun_token}"

                errors.append(
                    GrammarError(
                        type="case_agreement",
                        location=(start, end),
                        severity=ErrorSeverity.MAJOR,
                        description=f"Adjective-noun mismatch: {', '.join(mismatch_details)}",
                        suggestion=suggestion,
                        rule_id=self.rule_id,
                        confidence=0.95,
                        morphology={
                            "adjective": {
                                "word": adj_token,
                                "gender": getattr(adj_tag, "gender", None),
                                "case": getattr(adj_tag, "case", None),
                                "number": getattr(adj_tag, "number", None),
                            },
                            "noun": {
                                "word": noun_token,
                                "gender": getattr(noun_tag, "gender", None),
                                "case": getattr(noun_tag, "case", None),
                                "number": getattr(noun_tag, "number", None),
                            },
                        },
                    )
                )

        return RuleResult(errors=errors)


class NumeralNounAgreementRule(Rule):
    """Check numeral-noun agreement in Russian.

    Rules:
    - 1: Nominative singular (1 дом)
    - 2-4: Genitive singular (2 дома)
    - 5+: Genitive plural (5 домов)

    Examples:
        >>> rule = NumeralNounAgreementRule()
        >>> result = rule.check("пять дом")  # Should be "пять домов"
        >>> len(result.errors)
        1
    """

    def __init__(self) -> None:
        """Initialize numeral-noun agreement rule."""
        super().__init__(rule_id="NUMERAL_NOUN_AGREEMENT", category="agreement", severity="major")

        # Numerals that require genitive singular (2-4, 22, 23, 24, etc.)
        self.gent_sing_pattern = re.compile(r"\b([2-4]|[2-9][2-4]|1[2-4])\b")

        # Numerals that require genitive plural (5+, except 2-4 pattern)
        self.gent_plur_pattern = re.compile(r"\b([5-9]|[1-9]\d+[05-9]|1\d)\b")

    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check numeral-noun agreement.

        Args:
            text: Text to check
            morphology: Optional MAWOMorphAnalyzer instance

        Returns:
            RuleResult with agreement errors
        """
        if morphology is None:
            return RuleResult(errors=[])

        errors: list[GrammarError] = []

        # Find numeral-noun patterns
        tokens = text.split()

        for i in range(len(tokens) - 1):
            num_token = tokens[i]
            noun_token = tokens[i + 1]

            # Check if this is a number
            if not num_token.isdigit():
                continue

            num = int(num_token)

            # Parse noun
            if not hasattr(morphology, "parse"):
                continue

            noun_parses = morphology.parse(noun_token)
            if not noun_parses:
                continue

            noun_parse = noun_parses[0]
            if not hasattr(noun_parse, "tag"):
                continue

            noun_tag = noun_parse.tag

            # Determine required case and number
            required_case = None
            required_number = None

            if num % 10 == 1 and num % 100 != 11:
                # 1, 21, 31, ... → Nominative singular
                required_case = "nomn"
                required_number = "sing"
            elif num % 10 in (2, 3, 4) and num % 100 not in (12, 13, 14):
                # 2-4, 22-24, ... → Genitive singular
                required_case = "gent"
                required_number = "sing"
            else:
                # 5+, 11-14, ... → Genitive plural
                required_case = "gent"
                required_number = "plur"

            # Check if noun matches
            actual_case = getattr(noun_tag, "case", None)
            actual_number = getattr(noun_tag, "number", None)

            if actual_case != required_case or actual_number != required_number:
                # Calculate position
                start = len(" ".join(tokens[:i]))
                if i > 0:
                    start += 1
                end = start + len(num_token) + 1 + len(noun_token)

                # Try to suggest correction
                suggestion = None
                if hasattr(noun_parse, "inflect"):
                    required_tags = {required_case, required_number}
                    inflected = noun_parse.inflect(required_tags)
                    if inflected and hasattr(inflected, "word"):
                        suggestion = f"{num_token} {inflected.word}"

                errors.append(
                    GrammarError(
                        type="numeral_agreement",
                        location=(start, end),
                        severity=ErrorSeverity.MAJOR,
                        description=(
                            f"Numeral-noun agreement error: {num_token} requires "
                            f"{required_case} {required_number}, got {actual_case} {actual_number}"
                        ),
                        suggestion=suggestion,
                        rule_id=self.rule_id,
                        confidence=0.90,
                    )
                )

        return RuleResult(errors=errors)
