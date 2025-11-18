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
        # Note: PyMorphy3 uses "ablt" (ablative) for instrumental case, so we include both
        self.preposition_cases = {
            # Genitive
            "без": ["gent"],
            "для": ["gent"],
            "до": ["gent"],
            "из": ["gent"],
            "от": ["gent"],
            "у": ["gent"],
            "с": ["gent", "accs", "ins", "ablt"],  # Multiple cases possible, ablt=ins
            # Dative
            "к": ["datv"],
            "по": ["datv", "accs"],  # Multiple cases
            # Accusative
            "про": ["accs"],
            "через": ["accs"],
            "в": ["accs", "loct"],  # в + acc (motion) or loc (location)
            "на": ["accs", "loct"],  # на + acc (motion) or loc (location)
            "за": ["accs", "ins", "ablt"],  # ablt=ins
            "под": ["accs", "ins", "ablt"],  # ablt=ins
            # Instrumental
            "над": ["ins", "ablt"],  # ablt=ins
            "перед": ["ins", "ablt"],  # ablt=ins
            "между": ["ins", "ablt"],  # ablt=ins
            # Prepositional
            "о": ["loct"],
            "об": ["loct"],
            "при": ["loct"],
        }

    # Instrumental forms of pronouns that PyMorphy3 sometimes misidentifies
    # These words are obviously instrumental (with whom? with what?)
    PRONOUN_INSTRUMENTAL_FORMS = {
        "мной",
        "мною",  # я (I)
        "тобой",
        "тобою",  # ты (you)
        "им",
        "ею",
        "ей",
        "ним",
        "нею",  # он, она, оно (he, she, it)
        "нами",  # мы (we)
        "вами",  # вы (you plural)
        "ими",
        "ними",  # они (they)
        "кем",  # кто (who)
        "чем",  # что (what)
        "собой",
        "собою",  # себя (oneself)
        "всеми",  # все (all)
        "теми",  # те (those)
        "этим",
        "этими",  # это/эти (this/these)
        "тем",
        "той",
        "теми",  # тот/та/то/те (that/those)
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
            prep_token = tokens[i].strip(",.!?;:\"'()[]{}«»").lower()
            noun_token = tokens[i + 1].strip(",.!?;:\"'()[]{}«»")

            # Skip if tokens are empty or too short
            if not prep_token or not noun_token or len(noun_token) < 2:
                continue

            # Check if this is a known preposition
            if prep_token not in self.preposition_cases:
                continue

            # Parse the following noun
            noun_parses = morphology.parse(noun_token)
            if not noun_parses:
                continue

            # Get required cases for this preposition
            required_cases = self.preposition_cases[prep_token]

            # DEFENSIVE: If we only get 1 parse, it might be incomplete (wrapper limitation)
            # For neuter inanimate nouns, nominative = accusative (same form)
            # If we got nomn and need accs, check if this could be a neuter noun
            if len(noun_parses) == 1:
                only_parse = noun_parses[0]
                if hasattr(only_parse, "tag"):
                    tag = only_parse.tag
                    gender = getattr(tag, "gender", None)
                    case = getattr(tag, "case", None)
                    animacy = getattr(tag, "animacy", None)

                    # Neuter inanimate: nomn == accs
                    # Note: animacy can be None or 'inan' for inanimate nouns
                    if gender == "neut" and case == "nomn" and animacy in (None, "inan"):
                        if "accs" in required_cases:
                            # This is likely correct (nomn = accs for neuter inanimate)
                            continue

            # Skip word fragments from line breaks
            # Example: "принц\nипам" → tokens = ["принц", "ипам"]
            # "ипам" is not a real word, it's a fragment!
            #
            # Conservative filter: Skip if word is short OR has low score
            noun_score = getattr(noun_parses[0], "score", 1.0)
            if len(noun_token) < 5 or noun_score < 0.5:
                # Short word or low confidence - might be fragment
                continue  # Skip to avoid false positives

            # Special case: Pronoun instrumental forms
            # PyMorphy3 sometimes misidentifies these, but they're obviously correct
            # Examples: "перед теми", "с ними", "между нами"
            if noun_token.lower() in self.PRONOUN_INSTRUMENTAL_FORMS:
                # If preposition requires instrumental/ablative, this is correct
                if "ins" in required_cases or "ablt" in required_cases:
                    continue  # Pronoun instrumental form is correct

            # CRITICAL FIX: Check ALL parses, not just the first one!
            # If ANY parse has the required case, it's correct.
            #
            # Example: "электронный адрес"
            # - "электронный" can be: nomn, gent, accs (homonymy)
            # - Context: "без их явного разрешения" requires gent
            # - We need to check if ANY parse is gent, not just first!

            found_correct_case = False
            actual_cases = []

            for noun_parse in noun_parses:
                if not hasattr(noun_parse, "tag"):
                    continue

                noun_tag = noun_parse.tag

                # Check if it's a noun/adjective
                if not hasattr(noun_tag, "POS") or noun_tag.POS not in (
                    "NOUN",
                    "NPRO",
                    "ADJF",
                    "ADJS",
                    "PRTF",
                ):
                    continue

                # Get actual case
                actual_case = getattr(noun_tag, "case", None)
                if actual_case is None:
                    continue

                actual_cases.append(actual_case)

                # Check if this parse has the required case
                if actual_case in required_cases:
                    found_correct_case = True
                    break  # Found correct case, no error

            # If we found at least one parse with correct case, skip
            if found_correct_case:
                continue

            # No parse with correct case found - report error
            if not actual_cases:
                continue  # No valid parses at all

            # Use the first parse for error reporting
            noun_parse = noun_parses[0]
            noun_tag = noun_parse.tag if hasattr(noun_parse, "tag") else None
            actual_case = actual_cases[0] if actual_cases else None

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
