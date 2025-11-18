"""
YAML Rule Loader for Russian Grammar Checker

Loads rules from YAML database and converts them to executable Rule objects.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from ..errors import GrammarError
from .base import Rule, RuleResult


class YAMLRule(Rule):
    """Rule loaded from YAML configuration."""

    def __init__(
        self,
        rule_id: str,
        category: str,
        subcategory: str,
        severity: str,
        description: str,
        explanation: str,
        patterns: list[dict[str, Any]],
        confidence: float,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            rule_id=rule_id,
            category=category,
            severity=severity,
        )
        self.subcategory = subcategory
        self.description = description
        self.explanation = explanation
        self.patterns = patterns
        self.confidence = confidence
        self.extra_data = kwargs

    def check(self, text: str, morphology: Any = None) -> RuleResult:
        """Check text against this rule's patterns."""
        errors: list[GrammarError] = []

        for pattern_config in self.patterns:
            # Pattern-based checking
            if "pattern" in pattern_config:
                pattern_errors = self._check_pattern(text, pattern_config, morphology)
                errors.extend(pattern_errors)

            # Morphology-based checking
            elif pattern_config.get("check_morphology"):
                morphology_errors = self._check_morphology(text, pattern_config, morphology)
                errors.extend(morphology_errors)

            # Dictionary-based checking
            elif "dictionary_words" in self.extra_data:
                dict_errors = self._check_dictionary(text, pattern_config)
                errors.extend(dict_errors)

        return RuleResult(errors=errors)

    def _check_pattern(
        self, text: str, pattern_config: dict[str, Any], morphology: Any
    ) -> list[GrammarError]:
        """Check text using regex pattern."""
        errors: list[GrammarError] = []
        pattern_str = pattern_config["pattern"]

        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for match in pattern.finditer(text):
                # Check if this is actually an error based on context
                if self._is_error(match, pattern_config, morphology, text):
                    suggestion = self._generate_suggestion(match, pattern_config)

                    error = GrammarError(
                        type=self.category,
                        location=(match.start(), match.end()),
                        severity=self.severity,
                        description=self.description,
                        suggestion=suggestion,
                        rule_id=self.rule_id,
                        confidence=self.confidence,
                    )
                    errors.append(error)
        except re.error:
            # Invalid regex pattern - skip this rule
            pass

        return errors

    def _is_error(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        """Determine if pattern match is actually an error."""
        # Check for exceptions
        if "exceptions" in pattern_config.get("examples", {}):
            matched_text = match.group(0).lower()
            for exception in pattern_config["examples"]["exceptions"]:
                if exception.lower() in matched_text:
                    return False

        # Check morphology if required
        if pattern_config.get("check_morphology") and morphology:
            return self._check_morphology_match(match, pattern_config, morphology)

        # Check case if required
        if pattern_config.get("check_case") and morphology:
            return self._check_case_match(match, pattern_config, morphology)

        # Check context markers
        if "check_context" in pattern_config or "check_context_markers" in pattern_config:
            return self._check_context_markers(match, pattern_config, text)

        # Default: pattern match is an error
        return True

    def _check_morphology_match(
        self, match: re.Match[str], pattern_config: dict[str, Any], morphology: Any
    ) -> bool:
        """Check if morphology matches expected values."""
        # Extract word after preposition/particle
        groups = match.groups()
        if len(groups) >= 2:
            word = groups[1]
            try:
                parses = morphology.parse(word)
                if not parses:
                    return False

                # Check if any parse matches expected case
                if "check_case" in pattern_config:
                    expected_case = pattern_config["check_case"]
                    return not any(expected_case in p.tag for p in parses)

                # Check if verb conjugation is correct
                if pattern_config.get("check_conjugation"):
                    # TODO: Implement conjugation checking
                    return False

            except Exception:
                return False

        return False

    def _check_case_match(
        self, match: re.Match[str], pattern_config: dict[str, Any], morphology: Any
    ) -> bool:
        """Check if case matches expected value."""
        groups = match.groups()
        if len(groups) >= 2:
            word = groups[1]
            expected_case = pattern_config["check_case"]

            try:
                parses = morphology.parse(word)
                if not parses:
                    return False

                # If none of the parses have the expected case, it's an error
                return not any(expected_case in p.tag for p in parses)
            except Exception:
                return False

        return False

    def _check_context_markers(
        self, match: re.Match[str], pattern_config: dict[str, Any], text: str
    ) -> bool:
        """Check for context markers that determine correctness."""
        markers = pattern_config.get("check_context_markers", [])
        if not markers:
            return True

        # Look for markers in surrounding context (50 chars before/after)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].lower()

        # Check if any marker is present
        return any(marker.lower() in context for marker in markers)

    def _generate_suggestion(
        self, match: re.Match[str], pattern_config: dict[str, Any]
    ) -> str | None:
        """Generate correction suggestion."""
        # If there's a direct replacement specified
        if "correct" in pattern_config:
            correct = pattern_config["correct"]
            return str(correct) if correct is not None else None

        # If there are examples, try to infer suggestion
        if "examples" in pattern_config:
            examples = pattern_config["examples"]
            if "correct" in examples and examples["correct"]:
                # Return first correct example as suggestion
                first_example = examples["correct"][0]
                return str(first_example) if first_example is not None else None

        # Check if there's a replacement mapping
        if "replacements" in self.extra_data:
            matched_text = match.group(0).lower()
            for wrong, right in self.extra_data["replacements"].items():
                if wrong.lower() in matched_text:
                    return str(right) if right is not None else None

        return None

    def _check_morphology(
        self, text: str, pattern_config: dict[str, Any], morphology: Any
    ) -> list[GrammarError]:
        """Check using morphological analysis."""
        errors: list[GrammarError] = []

        if not morphology:
            return errors

        # This would require tokenization and morphological analysis
        # For now, return empty list - will be implemented with full integration
        # TODO: Implement morphology-based checking

        return errors

    def _check_dictionary(self, text: str, pattern_config: dict[str, Any]) -> list[GrammarError]:
        """Check against dictionary words."""
        errors: list[GrammarError] = []

        dictionary_words = self.extra_data.get("dictionary_words", [])
        text_lower = text.lower()

        for word in dictionary_words:
            # Simple word boundary check
            word_pattern = r"\b" + re.escape(word.lower()) + r"\b"
            for match in re.finditer(word_pattern, text_lower):
                # This is just checking if dictionary words exist
                # For spelling, we'd need to check if they're spelled correctly
                pass

        return errors


class YAMLRuleLoader:
    """Loads grammar rules from YAML configuration."""

    def __init__(self, rules_path: str | Path | None = None) -> None:
        if rules_path is None:
            # Default to rules.yml in data directory
            data_dir = Path(__file__).parent.parent / "data"
            rules_path = data_dir / "rules.yml"

        self.rules_path = Path(rules_path)
        self.rules: dict[str, list[YAMLRule]] = {}

    def load(self) -> dict[str, list[YAMLRule]]:
        """Load all rules from YAML file(s)."""
        # Load main rules file
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_path}")

        self._load_from_file(self.rules_path)

        # Load additional rules file if it exists
        additional_path = self.rules_path.parent / "rules_additional.yml"
        if additional_path.exists():
            self._load_from_file(additional_path)

        return self.rules

    def _load_from_file(self, file_path: Path) -> None:
        """Load rules from a specific YAML file."""
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            return

        # All possible categories (will auto-detect from YAML)
        # This includes both standard categories and new ones from additional file
        for category, rules_data in data.items():
            if category == "metadata":
                continue  # Skip metadata section

            if isinstance(rules_data, list):
                # Standard format: category: [list of rules]
                if category not in self.rules:
                    self.rules[category] = []
                self.rules[category].extend(self._load_category(category, rules_data))
            elif isinstance(rules_data, dict):
                # New format: top-level keys with nested rules
                # e.g., style_functional: {rules}, paronymes: {rules}
                if category not in self.rules:
                    self.rules[category] = []

                # Check if this is a dict of rules or a dict with rule list
                if any(isinstance(v, list) for v in rules_data.values()):
                    # Dict contains lists of rules (like additional file structure)
                    for subcategory, subrules in rules_data.items():
                        if isinstance(subrules, list):
                            self.rules[category].extend(self._load_category(category, subrules))
                else:
                    # Single dict rule - treat as one rule in list
                    self.rules[category].extend(self._load_category(category, [rules_data]))

    def _load_category(self, category: str, rules_data: list[dict[str, Any]]) -> list[YAMLRule]:
        """Load rules for a specific category."""
        rules: list[YAMLRule] = []

        for rule_data in rules_data:
            try:
                rule = YAMLRule(
                    rule_id=rule_data.get("id", f"{category}_rule"),
                    category=rule_data.get("category", category),
                    subcategory=rule_data.get("subcategory", "general"),
                    severity=rule_data.get("severity", "major"),
                    description=rule_data.get("description", ""),
                    explanation=rule_data.get("explanation", ""),
                    patterns=rule_data.get("patterns", []),
                    confidence=rule_data.get("confidence", 0.9),
                    # Pass any extra fields
                    **{
                        k: v
                        for k, v in rule_data.items()
                        if k
                        not in [
                            "id",
                            "category",
                            "subcategory",
                            "severity",
                            "description",
                            "explanation",
                            "patterns",
                            "confidence",
                        ]
                    },
                )
                rules.append(rule)
            except Exception as e:
                # Skip malformed rules but log error
                print(f"Warning: Failed to load rule {rule_data.get('id', 'unknown')}: {e}")
                continue

        return rules

    def get_rules_by_category(self, category: str) -> list[YAMLRule]:
        """Get all rules for a specific category."""
        return self.rules.get(category, [])

    def get_all_rules(self) -> list[YAMLRule]:
        """Get all loaded rules."""
        all_rules: list[YAMLRule] = []
        for category_rules in self.rules.values():
            all_rules.extend(category_rules)
        return all_rules

    def get_rule_by_id(self, rule_id: str) -> YAMLRule | None:
        """Get a specific rule by its ID."""
        for category_rules in self.rules.values():
            for rule in category_rules:
                if rule.rule_id == rule_id:
                    return rule
        return None
