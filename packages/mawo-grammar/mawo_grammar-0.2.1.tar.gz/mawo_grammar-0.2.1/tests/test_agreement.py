"""Tests for agreement rules."""

from __future__ import annotations

from mawo_grammar.rules import AdjNounAgreementRule, NumeralNounAgreementRule


class TestAdjNounAgreementRule:
    """Test suite for adjective-noun agreement rule."""

    def test_init(self) -> None:
        """Test rule initialization."""
        rule = AdjNounAgreementRule()
        assert rule.rule_id == "ADJ_NOUN_GENDER_AGREEMENT"
        assert rule.category == "agreement"

    def test_check_without_morphology(self) -> None:
        """Test checking without morphology analyzer."""
        rule = AdjNounAgreementRule()
        result = rule.check("красивая дом")

        # Should return empty errors without morphology
        assert len(result.errors) == 0

    def test_enabled(self) -> None:
        """Test rule is enabled."""
        rule = AdjNounAgreementRule()
        assert rule.enabled() is True


class TestNumeralNounAgreementRule:
    """Test suite for numeral-noun agreement rule."""

    def test_init(self) -> None:
        """Test rule initialization."""
        rule = NumeralNounAgreementRule()
        assert rule.rule_id == "NUMERAL_NOUN_AGREEMENT"
        assert rule.category == "agreement"

    def test_check_without_morphology(self) -> None:
        """Test checking without morphology analyzer."""
        rule = NumeralNounAgreementRule()
        result = rule.check("5 дом")

        # Should return empty errors without morphology
        assert len(result.errors) == 0
