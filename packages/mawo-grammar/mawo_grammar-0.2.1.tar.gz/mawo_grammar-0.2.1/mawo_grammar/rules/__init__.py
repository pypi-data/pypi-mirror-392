"""Grammar rules for Russian language."""

from __future__ import annotations

from .agreement import AdjNounAgreementRule, NumeralNounAgreementRule
from .aspect import VerbAspectRule
from .base import Rule, RuleResult
from .particles import ParticleUsageRule
from .prepositions import PrepositionCaseRule

__all__ = [
    "Rule",
    "RuleResult",
    "AdjNounAgreementRule",
    "NumeralNounAgreementRule",
    "VerbAspectRule",
    "ParticleUsageRule",
    "PrepositionCaseRule",
]
