"""Main grammar checker implementation."""

from __future__ import annotations

from typing import Any

from .errors import GrammarError
from .rules import (
    AdjNounAgreementRule,
    NumeralNounAgreementRule,
    ParticleUsageRule,
    PrepositionCaseRule,
    Rule,
    VerbAspectRule,
)
from .rules.yaml_loader import YAMLRuleLoader


class _MorphologyWrapper:
    """Wrapper around PyMorphy3 that uses mawo-core for better morphology.

    This wrapper provides the parse() API expected by rules but uses
    mawo-core internally for improved morphological analysis (prepositions,
    disambiguation, etc.)

    It caches full-text analysis to preserve context for disambiguation.
    """

    def __init__(self, fallback_analyzer: Any):
        """Initialize wrapper.

        Args:
            fallback_analyzer: PyMorphy3 analyzer to use as fallback
        """
        self._fallback = fallback_analyzer
        self._nlp = None
        self._cache: dict[str, Any] = {}  # Cache for full-text analysis
        self._current_text: str = ""

        # Try to import mawo-core
        try:
            from mawo import Russian  # type: ignore[import-not-found]

            self._nlp = Russian()
        except ImportError:
            import logging

            logging.warning("mawo-core not available, using PyMorphy3 directly")

    def analyze_text(self, text: str) -> None:
        """Pre-analyze full text with context for better disambiguation.

        Args:
            text: Full text to analyze
        """
        if self._nlp is None:
            return

        self._current_text = text
        self._cache = {}

        # Analyze full text with context
        doc = self._nlp(text)

        # Cache morphology for each token by its text
        for token in doc.tokens:
            # Use text as key, but handle duplicates by storing as list
            if token.text not in self._cache:
                self._cache[token.text] = []

            if hasattr(token, "_morphology") and token._morphology:
                self._cache[token.text].append(token._morphology)

    def parse(self, word: str) -> list[Any]:
        """Parse word using cached mawo-core analysis or fallback.

        Args:
            word: Word to parse

        Returns:
            List of parse results compatible with PyMorphy3 API
        """
        # Try to use cached analysis first (preserves context)
        if word in self._cache and self._cache[word]:
            # Return first cached parse (duplicates handled)
            cached = self._cache[word]
            if cached:
                result = cached.pop(0)  # Pop to handle duplicates correctly
                return [result]

        # Fallback to PyMorphy3
        fallback_result: list[Any] = self._fallback.parse(word)
        return fallback_result


class RussianGrammarChecker:
    """Russian grammar checker with 500+ rules.

    Provides comprehensive grammar checking for Russian text including:
    - Case agreement (adjective-noun, numeral-noun)
    - Verb aspect validation
    - Particle usage
    - Preposition + case rules
    - Register consistency

    Example:
        >>> checker = RussianGrammarChecker()
        >>> errors = checker.check("красивая дом")
        >>> print(errors[0].description)
        'Adjective-noun mismatch: gender: fem vs masc'
    """

    def __init__(self) -> None:
        """Initialize Russian grammar checker with default rules."""
        self.rules: list[Rule] = []
        self._morphology_analyzer: Any = None

        # Register default rules
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default grammar rules."""
        # Legacy hardcoded rules
        self.rules = [
            # Agreement rules
            AdjNounAgreementRule(),
            NumeralNounAgreementRule(),
            # Aspect rules
            VerbAspectRule(),
            # Particle rules
            ParticleUsageRule(),
            # Preposition rules
            PrepositionCaseRule(),
        ]

        # Load YAML rules (540+ additional rules)
        try:
            loader = YAMLRuleLoader()
            yaml_rules = loader.load()

            # Add all YAML rules to the rules list
            for category_rules in yaml_rules.values():
                self.rules.extend(category_rules)

            import logging

            total_yaml_rules = sum(len(rules) for rules in yaml_rules.values())
            logging.info(f"Loaded {total_yaml_rules} YAML rules")
        except Exception as e:
            import logging

            logging.warning(f"Failed to load YAML rules: {e}")

    def check(
        self,
        text: str,
        rules: list[str] | None = None,
        morphology: Any = None,
    ) -> list[GrammarError]:
        """Check text for grammar errors.

        Args:
            text: Text to check
            rules: Optional list of rule categories to apply
                   (e.g., ['case_agreement', 'aspect_usage'])
                   If None, applies all rules
            morphology: Optional morphology analyzer (MAWOMorphAnalyzer)
                       If None, tries to create one

        Returns:
            List of grammar errors found

        Example:
            >>> errors = checker.check("красивая дом")
            >>> len(errors)
            1

            >>> errors = checker.check(text, rules=['case_agreement'])
            >>> # Only case agreement errors
        """
        # Get or create morphology analyzer
        if morphology is None:
            morphology = self._get_morphology_analyzer()

        # Pre-analyze text with full context (if using wrapper)
        if hasattr(morphology, "analyze_text"):
            morphology.analyze_text(text)

        # Filter rules if specified
        if rules is not None:
            active_rules = [r for r in self.rules if r.category in rules]
        else:
            active_rules = self.rules

        # Apply rules and collect errors
        all_errors: list[GrammarError] = []

        for rule in active_rules:
            if not rule.enabled():
                continue

            try:
                result = rule.check(text, morphology=morphology)
                all_errors.extend(result.errors)
            except Exception as e:
                # Log error but continue with other rules
                import logging

                logging.warning(f"Rule {rule.rule_id} failed: {e}")
                continue

        # Sort errors by location
        all_errors.sort(key=lambda e: e.location[0])

        return all_errors

    def check_with_morphology(
        self,
        text: str,
        morphology: Any,
    ) -> list[GrammarError]:
        """Check text using provided morphology analyzer.

        Args:
            text: Text to check
            morphology: MAWOMorphAnalyzer instance

        Returns:
            List of grammar errors
        """
        return self.check(text, morphology=morphology)

    def add_rule(self, rule: Rule) -> None:
        """Add a custom grammar rule.

        Args:
            rule: Rule instance to add

        Example:
            >>> from mawo_grammar.rules import Rule, RuleResult
            >>> class MyCustomRule(Rule):
            ...     def check(self, text, morphology=None):
            ...         return RuleResult(errors=[])
            >>> checker.add_rule(MyCustomRule())
        """
        self.rules.append(rule)

    def _get_morphology_analyzer(self) -> Any:
        """Get or create morphology analyzer with mawo-core improvements.

        Returns:
            Morphology analyzer compatible with parse() API
        """
        if self._morphology_analyzer is None:
            try:
                from mawo_pymorphy3 import create_analyzer

                # Create base PyMorphy3 analyzer
                base_analyzer = create_analyzer()

                # Wrap it with mawo-core improvements (prepositions, disambiguation)
                self._morphology_analyzer = _MorphologyWrapper(base_analyzer)

                import logging

                logging.info(
                    "Using enhanced morphology analyzer " "(PyMorphy3 + mawo-core improvements)"
                )
            except ImportError:
                import logging

                logging.warning(
                    "mawo-pymorphy3 not installed. "
                    "Install it for full grammar checking: pip install mawo-pymorphy3"
                )
                return None

        return self._morphology_analyzer

    def __repr__(self) -> str:
        """String representation."""
        return f"<RussianGrammarChecker with {len(self.rules)} rules>"
