"""Verb aspect rules for Russian grammar.

Validates usage of perfective and imperfective aspects based on context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..errors import ErrorSeverity, GrammarError
from .base import Rule, RuleResult

if TYPE_CHECKING:
    pass


class VerbAspectRule(Rule):
    """Check verb aspect appropriateness in context.

    Russian verbs have two aspects:
    - Perfective (совершенный вид): completed, single actions
    - Imperfective (несовершенный вид): ongoing, repeated actions

    Examples:
        - "Я прочитал книгу" (perfective) - completed action
        - "Я читал книгу" (imperfective) - process, no emphasis on completion
    """

    def __init__(self) -> None:
        """Initialize verb aspect rule."""
        super().__init__(
            rule_id="VERB_ASPECT_USAGE",
            category="aspect",
            severity="minor",  # Aspect choice can be subjective
        )

        # Perfectivizing prefixes (make verbs perfective)
        self.perfective_prefixes = {
            "вз",
            "вс",
            "вы",
            "до",
            "за",
            "из",
            "ис",
            "на",
            "о",
            "об",
            "от",
            "пере",
            "по",
            "под",
            "при",
            "про",
            "раз",
            "рас",
            "с",
            "у",
        }

    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check verb aspect usage.

        Args:
            text: Text to check
            morphology: Optional MAWOMorphAnalyzer instance

        Returns:
            RuleResult with aspect errors
        """
        if morphology is None:
            return RuleResult(errors=[])

        errors: list[GrammarError] = []
        tokens = text.split()

        if not hasattr(morphology, "parse"):
            return RuleResult(errors=[])

        for i, token in enumerate(tokens):
            parses = morphology.parse(token)
            if not parses:
                continue

            parse = parses[0]
            if not hasattr(parse, "tag"):
                continue

            tag = parse.tag

            # Check if this is a verb
            if not hasattr(tag, "POS") or tag.POS not in ("VERB", "INFN"):
                continue

            # Get aspect
            aspect = getattr(tag, "aspect", None)
            if aspect is None:
                continue

            # Context-based validation (simplified)
            # In real implementation, this would analyze surrounding context

            # Example: Check for markers of completed action
            has_completion_marker = False
            if i > 0:
                prev_token = tokens[i - 1].lower()
                # Markers suggesting perfective: уже, только что, наконец
                if prev_token in ("уже", "наконец"):
                    has_completion_marker = True

            # If we have completion marker but imperfective verb
            if has_completion_marker and aspect == "impf":
                start = len(" ".join(tokens[:i]))
                if i > 0:
                    start += 1
                end = start + len(token)

                # Try to suggest perfective form
                suggestion = None
                normal_form = getattr(parse, "normal_form", token)

                # Simple heuristic: add perfective prefix if not present
                # In real implementation, use aspect pair dictionary
                if not any(normal_form.startswith(prefix) for prefix in self.perfective_prefixes):
                    # This is a rough suggestion - real implementation needs aspect pair lookup
                    suggestion = f"Consider perfective aspect (e.g., по{normal_form})"

                errors.append(
                    GrammarError(
                        type="aspect_usage",
                        location=(start, end),
                        severity=ErrorSeverity.MINOR,  # Subjective
                        description=(
                            f"Consider perfective aspect with completion marker '{prev_token}'"
                        ),
                        suggestion=suggestion,
                        rule_id=self.rule_id,
                        confidence=0.60,  # Lower confidence for aspect checks
                        morphology={
                            "verb": token,
                            "aspect": aspect,
                            "context": "completion_marker",
                        },
                    )
                )

        return RuleResult(errors=errors)
