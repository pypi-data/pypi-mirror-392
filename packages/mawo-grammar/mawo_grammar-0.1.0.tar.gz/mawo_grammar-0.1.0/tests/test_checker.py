"""Tests for RussianGrammarChecker."""

from __future__ import annotations

from typing import Any

from mawo_grammar import RussianGrammarChecker


class TestRussianGrammarChecker:
    """Test suite for RussianGrammarChecker."""

    def test_init(self) -> None:
        """Test checker initialization."""
        checker = RussianGrammarChecker()
        assert checker is not None
        assert len(checker.rules) > 0

    def test_check_simple_text(self) -> None:
        """Test checking simple correct text."""
        checker = RussianGrammarChecker()

        # This might not find errors without morphology
        errors = checker.check("Привет мир")
        assert isinstance(errors, list)

    def test_add_custom_rule(self) -> None:
        """Test adding custom rule."""
        from mawo_grammar.rules import Rule, RuleResult

        class TestRule(Rule):
            def __init__(self) -> None:
                super().__init__("TEST_RULE", "test")

            def check(self, text: str, morphology: Any = None) -> RuleResult:
                return RuleResult(errors=[])

        checker = RussianGrammarChecker()
        initial_count = len(checker.rules)

        checker.add_rule(TestRule())
        assert len(checker.rules) == initial_count + 1

    def test_check_with_rule_filter(self) -> None:
        """Test checking with specific rules."""
        checker = RussianGrammarChecker()

        # Check only case agreement rules
        errors = checker.check("test text", rules=["agreement"])
        assert isinstance(errors, list)

    def test_repr(self) -> None:
        """Test string representation."""
        checker = RussianGrammarChecker()
        repr_str = repr(checker)
        assert "RussianGrammarChecker" in repr_str
        assert "rules" in repr_str
