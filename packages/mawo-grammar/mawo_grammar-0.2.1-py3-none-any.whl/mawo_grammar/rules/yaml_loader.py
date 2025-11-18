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

# Phraseological expressions with gerunds that don't need commas
GERUND_PHRASEOLOGISMS = {
    "сломя голову",
    "очертя голову",
    "спустя рукава",
    "засучив рукава",
    "не покладая рук",
    "сложа руки",
    "высунув язык",
    "затаив дыхание",
    "не переводя духа",
    "уставясь в потолок",
    "не помня себя",
    "не смыкая глаз",
    "развесив уши",
    "скрепя сердце",
    "положив руку на сердце",
    "сидеть сложа руки",
    "работать не покладая рук",
    "бежать сломя голову",
}

# Special gerund-like words that are commonly used without commas in modern Russian
# "включая" (including) is often used without comma in enumerations
GERUND_PARTICLES = {
    "включая",  # including - comma is optional in modern Russian
    "исключая",  # excluding - comma is optional
    "начиная",  # starting from - comma is optional
    "кончая",  # ending with - comma is optional
}

# Russian consonants classification for prefix rules
VOICED_CONSONANTS = set("бвгджзйлмнр")  # Звонкие
VOICELESS_CONSONANTS = set("кпстфхцчшщ")  # Глухие

# Idiomatic expressions with "в" that use prepositional case (fixed expressions)
IDIOMS_V_PREPOSITIONAL = {
    "в ответ",
    "в течение",
    "в качестве",
    "в рамках",
    "в связи",
    "в отличие",
    "в результате",
    "в случае",
    "в ходе",
    "в частности",
    "в силу",
    "в целом",
    "в основном",
    "в первую очередь",
}

# Idiomatic expressions with "на" that use prepositional case
IDIOMS_NA_PREPOSITIONAL = {
    "на основе",
    "на основании",
    "на примере",
}

# Motion verbs (глаголы движения) - require accusative
MOTION_VERBS = {
    "идти",
    "ходить",
    "пойти",
    "прийти",
    "приходить",
    "ехать",
    "ездить",
    "поехать",
    "приехать",
    "приезжать",
    "бежать",
    "бегать",
    "побежать",
    "лететь",
    "летать",
    "полететь",
    "плыть",
    "плавать",
    "поплыть",
    "нести",
    "носить",
    "принести",
    "приносить",
    "везти",
    "возить",
    "привезти",
    "привозить",
    "вести",
    "водить",
    "привести",
    "приводить",
    "войти",
    "входить",
    "выйти",
    "выходить",
    "зайти",
    "заходить",
    "уйти",
    "уходить",
    "переходить",
    "перейти",
    "переехать",
    "переезжать",
    "отправиться",
    "отправляться",
    "направиться",
    "направляться",
    "двигаться",
    "передвигаться",
    "перемещаться",
    "вернуться",
    "возвращаться",
    "попасть",
    "попадать",
    "поместить",
    "помещать",
    "положить",
    "класть",
    "посадить",
    "сажать",
    "поставить",
    "ставить",
    "вставить",
    "вставлять",
    "добавить",
    "добавлять",
    "внести",
    "вносить",
    "включить",
    "включать",
}

# Location/state verbs (глаголы состояния) - require prepositional
LOCATION_VERBS = {
    "быть",
    "находиться",
    "оказаться",
    "остаться",
    "оставаться",
    "жить",
    "проживать",
    "обитать",
    "пребывать",
    "работать",
    "трудиться",
    "служить",
    "учиться",
    "обучаться",
    "заниматься",
    "сидеть",
    "стоять",
    "лежать",
    "висеть",
    "располагаться",
    "размещаться",
    "существовать",
    "присутствовать",
    "участвовать",
}


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
        # Check for phraseological expressions first
        matched_text = match.group(0)
        for phrase in GERUND_PHRASEOLOGISMS:
            if phrase in text[max(0, match.start() - 20) : match.end() + 20].lower():
                return False  # Not an error - it's a phraseologism

        # Check for exceptions
        if "exceptions" in pattern_config.get("examples", {}):
            matched_text_lower = matched_text.lower()
            for exception in pattern_config["examples"]["exceptions"]:
                if exception.lower() in matched_text_lower:
                    return False

        # Check if this is actually a gerund (CRITICAL FIX!)
        if pattern_config.get("check_gerund") and morphology:
            return self._check_gerund(match, pattern_config, morphology, text)

        # Check consonant after prefix (for PREFIX_Z_S rule)
        if pattern_config.get("check_next_consonant"):
            return self._check_prefix_consonant(match, pattern_config, text)

        # Check same root for tautology
        if pattern_config.get("check_same_root") and morphology:
            return self._check_tautology(match, pattern_config, morphology, text)

        # Check verb conjugation
        if pattern_config.get("check_conjugation") and morphology:
            return self._check_verb_conjugation(match, pattern_config, morphology)

        # Check for separate predicates (complex sentence with multiple clauses)
        if pattern_config.get("check_separate_predicates") and morphology:
            return self._check_separate_predicates(match, pattern_config, morphology, text)

        # Check homogeneous members (enumeration with commas)
        if pattern_config.get("check_homogeneous"):
            # Pattern matched comma-separated list, which means commas ARE present
            # This is NOT an error - commas are already there!
            # Rule should match lists WITHOUT commas, not lists WITH commas
            return False  # Commas present = correct, no error

        # COMPOUND_SEPARATE_ADVERBS: Rule pattern finds CORRECT separate writing
        # Pattern: в\s+течение finds "в течение" which is CORRECT (раздельно)
        # Wrong pattern design - it should find "втечение" (слитно) instead
        # For now, skip all matches as they are correct
        if self.rule_id == "COMPOUND_SEPARATE_ADVERBS":
            return False  # Pattern finds correct writing, not errors

        # SOFT_SIGN_VERBS_3PERSON: Rule pattern finds CORRECT 3rd person forms (without Ь)
        # Pattern: ([а-яё]+)(ет|ит|ёт|ат|ят)ся finds "применяется" which is CORRECT
        # Wrong pattern design - it should find "применяеться" (с Ь) instead
        # For now, skip all matches as they are correct
        if self.rule_id == "SOFT_SIGN_VERBS_3PERSON":
            return False  # Pattern finds correct forms, not errors

        # SOFT_SIGN_VERBS_INFINITIVE: Rule pattern finds CORRECT infinitives (with Ь)
        # Pattern: ([а-яё]+ть|[а-яё]+ти|[а-яё]+чь)ся finds "потребоваться" which is CORRECT
        # Wrong pattern design - it should find "потребоватся" (без Ь) instead
        # For now, skip all matches as they are correct
        if self.rule_id == "SOFT_SIGN_VERBS_INFINITIVE":
            return False  # Pattern finds correct forms, not errors

        # NE_WITH_ADJECTIVES_TOGETHER: Rule pattern finds CORRECT forms (слитно)
        # Pattern: \b(не)([а-яё]+ый|[а-яё]+ий|[а-яё]+ой)\b finds "невидимой" which is CORRECT
        # Examples show "небольшой" as correct (слитно)
        # Wrong pattern design - it should find "не видимой" (раздельно) instead
        # For now, skip all matches as they are correct
        if self.rule_id == "NE_WITH_ADJECTIVES_TOGETHER":
            return False  # Pattern finds correct forms, not errors

        # Check motion (for в/на + accusative rules)
        if pattern_config.get("check_motion") and morphology:
            return self._check_motion_required(match, pattern_config, morphology, text)

        # Check location (for в/на + prepositional rules)
        if pattern_config.get("check_location") and morphology:
            return self._check_location_required(match, pattern_config, morphology, text)

        # Check if lemma exists without "не" (for NE_WITH_VERBS rule)
        if pattern_config.get("check_lemma_exists") and morphology:
            return self._check_lemma_without_ne(match, pattern_config, morphology)

        # Check prefix meaning (пре/при)
        if pattern_config.get("check_meaning"):
            # Not implemented yet - skip to avoid false positives
            return False

        # Check morphology if required
        if pattern_config.get("check_morphology") and morphology:
            return self._check_morphology_match(match, pattern_config, morphology)

        # Check case if required
        if pattern_config.get("check_case") and morphology:
            return self._check_case_match(match, pattern_config, morphology)

        # Check imperative vs future (for VERB_IMPERATIVE_VS_FUTURE rule)
        check_context = pattern_config.get("check_context")
        if check_context == "imperative_markers" and morphology:
            return self._check_imperative_vs_future(match, pattern_config, morphology, text)

        # Check particle ТАКИ (to avoid confusing with adjective таких/такой/etc)
        if self.rule_id == "PARTICLE_TAKI_EMPHASIS" and morphology:
            return self._check_particle_taki(match, pattern_config, morphology)

        # Check comma before subordinate conjunction (to avoid flagging sentence start)
        if pattern_config.get("check_comma_before"):
            return self._check_comma_before_conjunction(match, pattern_config, text)

        # Check I/Y after prefix (to avoid flagging foreign words)
        if pattern_config.get("check_after_prefix"):
            return self._check_i_y_after_prefix(match, pattern_config)

        # Check comparative КАК (to avoid flagging markdown headings)
        if pattern_config.get("check_comparative"):
            return self._check_comparative_kak(match, pattern_config, text)

        # Check context markers
        if "check_context" in pattern_config or "check_context_markers" in pattern_config:
            return self._check_context_markers(match, pattern_config, text)

        # Default: pattern match is an error
        return True

    def _check_gerund(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        """Check if matched word is actually a gerund (деепричастие).

        Returns True if it's an error (needs comma), False otherwise.
        """
        # Extract the word from the match (first capture group)
        groups = match.groups()
        if not groups:
            # No capture group - try whole match
            word = match.group(0).strip()
        else:
            word = groups[0].strip()

        # Skip empty words or punctuation
        if not word or len(word) < 2:
            return False

        # Clean the word (remove trailing punctuation)
        word = word.rstrip(",.!?;:")

        # Check for gerund particles (включая, исключая, etc.)
        # These are gerunds used as particles in modern Russian, comma is optional
        if word.lower() in GERUND_PARTICLES:
            return False  # Comma is optional, not an error

        # Skip prepositions that match the pattern (like "для")
        russian_prepositions = {
            "в",
            "во",
            "на",
            "с",
            "со",
            "к",
            "ко",
            "по",
            "за",
            "из",
            "изо",
            "о",
            "об",
            "обо",
            "от",
            "ото",
            "до",
            "для",
            "при",
            "про",
            "без",
            "безо",
            "под",
            "подо",
            "над",
            "надо",
            "перед",
            "передо",
            "у",
        }
        if word.lower() in russian_prepositions:
            return False

        # Skip demonstrative pronoun "такой" and its forms
        # Pattern sometimes catches "такая", "таких", "такое", etc.
        # These are NEVER gerunds!
        demonstrative_forms = {
            "такой",
            "такая",
            "такое",
            "такие",
            "таких",
            "такому",
            "такой",
            "таким",
            "такими",
            "такою",
        }
        if word.lower() in demonstrative_forms:
            return False  # Demonstrative pronoun, not gerund

        # Skip common nouns that pattern catches
        # Pattern catches words ending in -ия, -ая but many are nouns, not gerunds
        common_nouns_not_gerunds = {
            "зрения",  # vision (точка зрения = viewpoint)
            "мнения",  # opinion
            "знания",  # knowledge
            "желания",  # desire/wish
            "внимания",  # attention
            "дыхания",  # breathing (noun, not gerund)
        }
        if word.lower() in common_nouns_not_gerunds:
            return False  # Common noun, not gerund

        try:
            # Parse the word with morphology analyzer
            parses = morphology.parse(word)

            if not parses:
                return False

            # Check all possible parses for this word
            for parse in parses:
                if not hasattr(parse, "tag"):
                    continue

                tag = parse.tag

                # Check if POS is GRND (gerund/деепричастие)
                if hasattr(tag, "POS") and tag.POS == "GRND":
                    # It IS a gerund - check if comma is needed
                    # Comma is needed unless it's:
                    # 1. A phraseologism (already checked above)
                    # 2. Used as an adverb (like "читал лежа", "стоял молча")

                    # Check for adverbial usage (single gerund, no modifiers)
                    # Look for patterns like "verb + gerund" with no words between
                    context_before = text[max(0, match.start() - 30) : match.start()]
                    context_after = text[match.end() : min(len(text), match.end() + 10)]

                    # CRITICAL: Check if comma is ALREADY present before gerund
                    # Example: "изменения, следуя нашим стандартам" - comma before "следуя" ✓
                    # This is CORRECT, not an error!
                    if "," in context_before[-5:]:  # Check last 5 chars before gerund
                        return False  # Comma already present, not an error

                    # If gerund immediately follows a verb (like "читал лежа")
                    # This is simplified - in real impl would need better verb detection
                    if context_after.strip() and not context_after.strip()[0].isalpha():
                        # Gerund at end of clause/sentence - likely adverbial
                        # Examples: "читал лежа.", "сидел молча,"
                        for p in parses:
                            if hasattr(p, "tag") and hasattr(p.tag, "POS"):
                                if p.tag.POS in ("VERB", "INFN", "NOUN", "ADJF"):
                                    # Mixed POS - might be used as adverb
                                    return False

                    # It's a real gerund that needs comma
                    return True

            # NOT a gerund - it's a false positive (like "поведения" - genitive noun)
            return False

        except Exception as e:
            # On error, don't report (safer than false positive)
            import logging

            logging.debug(f"Error checking gerund '{word}': {e}")
            return False

    def _check_prefix_consonant(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        text: str,
    ) -> bool:
        """Check if prefix з/с matches following consonant.

        Rule: З before voiced consonants, С before voiceless.
        Returns True if ERROR (wrong prefix), False if correct.
        """
        groups = match.groups()
        if len(groups) < 2:
            return False

        prefix = groups[0].lower()  # раз, рас, без, бес, etc.
        rest = groups[1]  # rest of the word

        if not rest:
            return False

        # Skip if "rest" is too short - likely not a real prefix
        # Examples: "расы" (раса), "всех" (весь), "всего" (весь)
        if len(rest) < 3:
            return False

        # Common words that are NOT prefix-based (exceptions)
        full_word = (prefix + rest).lower()
        non_prefix_words = {
            "раса",
            "расы",
            "весь",
            "всё",
            "всего",
            "всей",
            "всех",
            "всем",
            "всеми",
            "все",
            "вся",
            "всю",
            "всякий",
            "всякая",
            "всякое",
            # всегда (always) - not a prefix-based word
            "всегда",
            # всемирный (worldwide) - все + мир, not prefix вс-
            "всемирный",
            "всемирная",
            "всемирное",
            "всемирные",
            "всемирного",
            "всемирной",
            "всемирному",
            "всемирную",
            "всемирным",
            "всемирных",
        }
        if full_word in non_prefix_words:
            return False

        # Get first letter after prefix
        first_letter = rest[0].lower()

        # Determine if prefix ends with з or с
        prefix_ends_z = prefix.endswith("з")
        prefix_ends_s = prefix.endswith("с")

        if not (prefix_ends_z or prefix_ends_s):
            return False  # Not a з/с prefix

        # Check if next letter is consonant
        if first_letter in VOICED_CONSONANTS:
            # Should be З before voiced
            if prefix_ends_s:
                return True  # ERROR: should be З, not С
            else:
                return False  # Correct: З before voiced
        elif first_letter in VOICELESS_CONSONANTS:
            # Should be С before voiceless
            if prefix_ends_z:
                return True  # ERROR: should be С, not З
            else:
                return False  # Correct: С before voiceless
        else:
            # Not a consonant (vowel) - always use З
            if prefix_ends_s:
                return True  # ERROR: should be З before vowel
            else:
                return False  # Correct: З before vowel

    def _check_tautology(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        """Check if this is real tautology (same root words) or false positive.

        Returns True if ERROR (real tautology), False otherwise.
        """
        # Pattern captures: ([а-яё]+)\s+\1
        # This catches EXACT word repetition, not same root

        groups = match.groups()
        if not groups:
            return False

        # Check if this is word boundary issue (like "и и" in "разработчики и лидеры")
        # Find the repeated part in text
        match_start = match.start()

        # Look before match to see if it's part of a longer word
        if match_start > 0:
            char_before = text[match_start - 1]
            if char_before.isalpha():
                # The first occurrence is part of a word (like "...ки и")
                return False  # Not tautology, just word ending

        # Extract both words from the match
        match_text = match.group(0)
        parts = match_text.split()

        if len(parts) != 2:
            return False

        word1, word2 = parts[0].lower(), parts[1].lower()

        # If words are identical AND short (1-2 letters), likely false positive
        if word1 == word2 and len(word1) <= 2:
            return False  # "и и", "в в", etc. - not tautology

        # If words are identical and longer, might be real tautology
        # But need to check if they're complete words, not parts
        if word1 == word2:
            # Check with morphology if available
            try:
                parses1 = morphology.parse(word1)
                parses2 = morphology.parse(word2)

                # If both parse as same POS and are real words, it's tautology
                if parses1 and parses2:
                    # Check if they're both content words (not just prepositions/conjunctions)
                    pos1 = (
                        parses1[0].tag.POS
                        if hasattr(parses1[0], "tag") and hasattr(parses1[0].tag, "POS")
                        else None
                    )
                    pos2 = (
                        parses2[0].tag.POS
                        if hasattr(parses2[0], "tag") and hasattr(parses2[0].tag, "POS")
                        else None
                    )

                    # Real tautology should be content words
                    if pos1 in ("NOUN", "VERB", "ADJF", "ADJS") and pos1 == pos2:
                        return True  # Real tautology

            except Exception:
                pass

        # Default: not tautology
        return False

    def _check_verb_conjugation(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
    ) -> bool:
        """Check if word with verb ending is actually a verb.

        Pattern matches words ending in -ешь, -ет, -ем, -ете, -ут, -ют, etc.
        But these endings also appear in adjectives like "нашем", "большем".

        Returns True if ERROR (wrong conjugation), False if correct or not a verb.
        """
        groups = match.groups()
        if len(groups) < 2:
            return False

        stem = groups[0]
        ending = groups[1]
        full_word = stem + ending

        try:
            # Parse the word
            parses = morphology.parse(full_word)

            if not parses:
                return False

            # Check if this is actually a verb
            is_verb = False
            for parse in parses:
                if not hasattr(parse, "tag"):
                    continue

                tag = parse.tag
                if hasattr(tag, "POS"):
                    # Check if it's a verb (VERB or INFN)
                    if tag.POS in ("VERB", "INFN"):
                        is_verb = True
                        break

            # If it's not a verb, don't report an error
            if not is_verb:
                return False

            # It IS a verb - now check conjugation (not implemented yet)
            # For now, assume conjugation is correct to avoid false positives
            return False

        except Exception:
            # On error, don't report
            return False

    def _check_separate_predicates(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        r"""Check if sentence has separate predicates (complex sentence).

        Complex sentence (сложное предложение) has multiple clauses with their own predicates.
        Simple coordination of words (simple enumeration) does NOT require comma.

        Pattern: ([а-яё]+)\s+(и|а|но|или|либо|да)\s+([а-яё]+)
        Groups: (word_before) (conjunction) (word_after)

        Returns True if ERROR (missing comma in complex sentence), False otherwise.
        """
        groups = match.groups()
        if len(groups) < 3:
            return False

        word_before = groups[0]  # Word immediately before conjunction
        conjunction = groups[1]  # и, а, но, или, либо, да
        word_after = groups[2]  # Word immediately after conjunction

        # Get broader context: 50 chars before and after match
        context_start = max(0, match.start() - 50)
        context_end = min(len(text), match.end() + 50)
        context_before = text[context_start : match.start()]
        context_after = text[match.end() : context_end]

        try:
            # Find predicates (verbs) in both parts
            predicate_before = self._find_predicate_in_context(
                context_before + " " + word_before, morphology
            )
            predicate_after = self._find_predicate_in_context(
                word_after + " " + context_after, morphology
            )

            # Check if both parts have predicates
            if predicate_before and predicate_after:
                # Both parts have verbs - this is likely a complex sentence
                # Check if they're DIFFERENT predicates (not the same verb)
                if predicate_before.lower() != predicate_after.lower():
                    # Different predicates - COMPLEX SENTENCE needs comma
                    # But check if comma is already there
                    # Look for comma before conjunction
                    comma_check_zone = text[
                        max(0, match.start() - 5) : match.start()
                        + len(word_before)
                        + len(conjunction)
                        + 5
                    ]
                    if "," in comma_check_zone:
                        # Comma already present
                        return False

                    # Missing comma in complex sentence
                    return True

            # NOT a complex sentence - it's simple coordination/enumeration
            # Examples:
            # - "разработчики и лидеры" - no predicates, simple enumeration
            # - "видимой или невидимой" - adjectives, no predicates
            # - "эмпатии и доброты" - nouns, no predicates
            return False

        except Exception as e:
            import logging

            logging.debug(f"Error checking predicates: {e}")
            # On error, don't report (safer than false positive)
            return False

    def _find_predicate_in_context(self, context: str, morphology: Any) -> str | None:
        """Find verb (predicate) in given context.

        Returns the verb word if found, None otherwise.
        """
        # Split context into words
        words = context.split()

        # Look for verbs (predicates) from right to left (closer to conjunction)
        for word in reversed(words):
            # Clean word from punctuation
            clean_word = word.strip(",.!?;:\"'()[]{}«»")
            if not clean_word or len(clean_word) < 2:
                continue

            try:
                parses = morphology.parse(clean_word)
                if not parses:
                    continue

                # Check if this word is a verb IN PERSONAL FORM (predicate)
                for parse in parses:
                    if not hasattr(parse, "tag"):
                        continue

                    tag = parse.tag
                    if hasattr(tag, "POS"):
                        # ONLY check for FINITE VERBS (personal forms) - true predicates!
                        # VERB - finite verb (делает, делал, будет делать) ✓ PREDICATE
                        #
                        # NOT predicates:
                        # INFN - infinitive (делать) ✗ NOT a predicate
                        # PRTS - short participle (сделан) ✗ usually adjective-like
                        # PRTF - full participle (сделанный) ✗ adjective-like
                        # GRND - gerund (делая) ✗ adverb-like
                        #
                        # Only VERB with mood (indicative, imperative) is a true predicate
                        if tag.POS == "VERB":
                            # Check that it has mood (finite form)
                            mood = getattr(tag, "mood", None)
                            if mood in ("indc", "impr"):  # Indicative or imperative
                                return clean_word

            except Exception:
                continue

        # No verb found
        return None

    def _check_motion_required(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        """Check if motion verb context requires accusative (куда?).

        Rule PREP_V_ACCUSATIVE_MOTION expects:
        - Motion verb (идти, ехать, войти, etc.) + в + accusative
        - Example: "идти в школу" (correct)
        - Counter: "быть в школе" (location, not motion)

        Returns True if ERROR (should be accusative but isn't), False otherwise.
        """
        groups = match.groups()
        if len(groups) < 2:
            return False

        noun_word = groups[1]

        # Check for idiomatic expressions first (они всегда prepositional)
        match_text = match.group(0).lower()
        for idiom in IDIOMS_V_PREPOSITIONAL:
            if idiom in match_text:
                return False  # Idiom - prepositional is correct, NOT motion

        # Get context before preposition (look for verb)
        context_start = max(0, match.start() - 50)
        context_before = text[context_start : match.start()]

        # Find verb in context
        words_before = context_before.split()
        found_motion_verb = False
        found_location_verb = False

        # Check last few words for verbs (closer to preposition)
        for word in reversed(words_before[-10:]):  # Last 10 words
            clean_word = word.strip(",.!?;:\"'()[]{}«»").lower()
            if not clean_word:
                continue

            # Check if it's a motion verb
            if clean_word in MOTION_VERBS:
                found_motion_verb = True
                break

            # Check if it's a location/state verb
            if clean_word in LOCATION_VERBS:
                found_location_verb = True
                break

            # Also check with morphology
            try:
                parses = morphology.parse(clean_word)
                if parses and hasattr(parses[0], "normal_form"):
                    lemma = parses[0].normal_form.lower()
                    if lemma in MOTION_VERBS:
                        found_motion_verb = True
                        break
                    if lemma in LOCATION_VERBS:
                        found_location_verb = True
                        break
            except Exception:
                continue

        # If location verb found, accusative would be WRONG
        if found_location_verb:
            return False  # Location context - prepositional is correct

        # If NO motion verb found, don't assume error
        # (could be nominal context, or verb is further away)
        if not found_motion_verb:
            return False  # No clear motion context - don't report

        # Motion verb found - check if noun is in accusative
        try:
            noun_parses = morphology.parse(noun_word)
            if not noun_parses:
                return False

            # CRITICAL: If noun is in prepositional (loct), it's LOCATION, not MOTION!
            # Example: "в пространствах" (loct) = where? (location)
            # NOT: "в пространства" (accs) = where to? (motion)
            has_prepositional = False
            has_accusative = False

            for parse in noun_parses:
                if not hasattr(parse, "tag"):
                    continue
                tag = parse.tag
                actual_case = getattr(tag, "case", None)

                if actual_case == "loct":  # Prepositional/locative
                    has_prepositional = True
                if actual_case == "accs":  # Accusative
                    has_accusative = True

            # If word is in prepositional, it's definitely LOCATION
            # Don't report error even if motion verb found
            # (maybe it's different clause, or different object)
            if has_prepositional and not has_accusative:
                return False  # Prepositional = location, not motion

            # Check if ANY parse has the required case
            if has_accusative:
                return False  # Correct case found

            # Motion verb + no accusative found + no prepositional = ERROR
            # (might be wrong case, like genitive or dative)
            return True

        except Exception:
            return False

    def _check_location_required(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        """Check if location verb context requires prepositional (где?).

        Rule PREP_V_PREPOSITIONAL_LOCATION expects:
        - Location verb (быть, находиться, жить, etc.) + в + prepositional
        - Example: "быть в школе" (correct)
        - Counter: "идти в школу" (motion, not location)

        Returns True if ERROR (should be prepositional but isn't), False otherwise.
        """
        groups = match.groups()
        if len(groups) < 2:
            return False

        noun_word = groups[1]

        # Check for idiomatic expressions (always prepositional - correct!)
        match_text = match.group(0).lower()
        idiom_sets = [IDIOMS_V_PREPOSITIONAL, IDIOMS_NA_PREPOSITIONAL]
        for idiom_set in idiom_sets:
            for idiom in idiom_set:
                if idiom in match_text:
                    # Check if it IS in prepositional (correct)
                    try:
                        noun_parses = morphology.parse(noun_word)
                        for parse in noun_parses:
                            if hasattr(parse, "tag"):
                                case = getattr(parse.tag, "case", None)
                                if case == "loct":
                                    return False  # Correct!
                    except Exception:
                        pass
                    return False  # Idiom - assume correct

        # Get context before preposition (look for verb)
        context_start = max(0, match.start() - 50)
        context_before = text[context_start : match.start()]

        # Find verb in context
        words_before = context_before.split()
        found_motion_verb = False
        found_location_verb = False

        # Check last few words for verbs
        for word in reversed(words_before[-10:]):
            clean_word = word.strip(",.!?;:\"'()[]{}«»").lower()
            if not clean_word:
                continue

            # Check if it's a location verb
            if clean_word in LOCATION_VERBS:
                found_location_verb = True
                break

            # Check if it's a motion verb
            if clean_word in MOTION_VERBS:
                found_motion_verb = True
                break

            # Also check with morphology
            try:
                parses = morphology.parse(clean_word)
                if parses and hasattr(parses[0], "normal_form"):
                    lemma = parses[0].normal_form.lower()
                    if lemma in LOCATION_VERBS:
                        found_location_verb = True
                        break
                    if lemma in MOTION_VERBS:
                        found_motion_verb = True
                        break
            except Exception:
                continue

        # If motion verb found, prepositional would be WRONG
        if found_motion_verb:
            return False  # Motion context - accusative is correct

        # If NO location verb found, don't assume error
        if not found_location_verb:
            return False  # No clear location context - don't report

        # Location verb found - check if noun is in prepositional
        required_case = pattern_config.get("check_case", "loct")

        try:
            noun_parses = morphology.parse(noun_word)
            if not noun_parses:
                return False

            # Check if ANY parse has the required case
            for parse in noun_parses:
                if not hasattr(parse, "tag"):
                    continue
                tag = parse.tag
                actual_case = getattr(tag, "case", None)
                if actual_case == required_case:
                    return False  # Correct case found

            # Location verb + no prepositional found = ERROR
            return True

        except Exception:
            return False

    def _check_lemma_without_ne(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
    ) -> bool:
        """Check if verb exists without НЕ particle.

        Rule NE_WITH_VERBS pattern: (не)([а-яё]+verb_ending)
        Problem: Matches "несут" thinking it's "не" + "сут"
        Reality: "несут" is "нести" (3rd person plural), NOT negation!

        Returns True if ERROR (НЕ should be separate), False otherwise.
        """
        groups = match.groups()
        if len(groups) < 2:
            return False

        ne_particle = groups[0]  # "не"
        verb_part = groups[1]  # supposed verb without "не"

        full_word = ne_particle + verb_part  # full matched word

        # Common verbs where "не" is part of root, not negation particle
        # These should NEVER be split
        verbs_with_ne_in_root = {
            # нести (to carry)
            "несу",
            "несёт",
            "несут",
            "нести",
            "нёс",
            "несла",
            "несли",
            # other verbs with не- prefix that are NOT negation
        }
        if full_word.lower() in verbs_with_ne_in_root:
            return False  # "не" is part of root, not separate particle

        try:
            # First, check if the FULL word (with "не") is a valid verb
            # Examples: "ненавидеть", "негодовать" exist as complete verbs
            full_parses = morphology.parse(full_word)

            for parse in full_parses:
                if not hasattr(parse, "tag"):
                    continue
                tag = parse.tag

                # If full word is a VERB, check if it exists without "не"
                if hasattr(tag, "POS") and tag.POS in ("VERB", "INFN"):
                    # This IS a verb - but is it a complete word or "не" + verb?

                    # Check lemma
                    lemma = getattr(parse, "normal_form", "").lower()

                    # If lemma starts with "не", it might be inseparable
                    # Examples: "ненавидеть", "негодовать", "недомогать"
                    if lemma.startswith("не"):
                        # Try to parse without "не"
                        without_ne = lemma[2:]  # Remove "не"
                        if len(without_ne) < 3:
                            # Too short to be a real verb
                            continue

                        # Check if base form exists
                        base_parses = morphology.parse(without_ne)
                        verb_exists = False
                        for bp in base_parses:
                            if hasattr(bp, "tag") and hasattr(bp.tag, "POS"):
                                if bp.tag.POS in ("VERB", "INFN"):
                                    verb_exists = True
                                    break

                        if verb_exists:
                            # Base verb EXISTS - "не" should be separate
                            # Example: "негодовать" → "годовать" exists → error
                            # But wait, "негодовать" is exception!
                            # Check exceptions
                            exceptions = pattern_config.get("examples", {}).get("exceptions", [])
                            if lemma in exceptions or full_word.lower() in exceptions:
                                return False  # Exception - write together

                            return True  # Error - should be "не годовать"
                        else:
                            # Base verb does NOT exist - must write together
                            # Example: "ненавидеть" → "навидеть" doesn't exist → OK
                            return False

                    # Lemma doesn't start with "не" - this might be wrong parse
                    # Example: "несут" parsed as "нести" (correct!)
                    # This means "не" is NOT a separate particle but part of root
                    # Don't report error
                    return False

            # Not a verb at all - don't report
            return False

        except Exception as e:
            import logging

            logging.debug(f"Error checking lemma without не: {e}")
            return False

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
            preposition = groups[0].lower() if groups[0] else ""
            word = groups[1]
            expected_case = pattern_config["check_case"]

            try:
                parses = morphology.parse(word)
                if not parses:
                    return False

                # Special handling for "с/со" preposition
                # "с/со" can take BOTH genitive (from) and instrumental (with)
                # Only flag error if word has NEITHER case
                if preposition in ("с", "со"):
                    has_genitive = any("gent" in str(p.tag) for p in parses)
                    has_instrumental = any(
                        "ablt" in str(p.tag) or "ins" in str(p.tag) for p in parses
                    )

                    # If word has genitive OR instrumental, it's correct with "с/со"
                    if has_genitive or has_instrumental:
                        return False  # Not an error

                    # If word has neither genitive nor instrumental, it's wrong
                    return True

                # For other prepositions, check expected case normally
                # If none of the parses have the expected case, it's an error
                return not any(expected_case in str(p.tag) for p in parses)
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

    def _check_imperative_vs_future(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
        text: str,
    ) -> bool:
        """Check imperative (-ите) vs future/present (-ете) verb forms.

        Returns True if it's an error (wrong form), False if correct.

        The rule:
        - -ИТЕ: imperative mood (напишите! - write!)
        - -ЕТЕ: future/present 2nd person plural (вы напишете - you will write)

        Problem: Present tense forms like "предоставляете", "имеете" are CORRECT
        and should NOT be flagged. This rule should ONLY flag genuine confusion
        between imperative and future.
        """
        # Extract the full verb
        verb = match.group(0).strip().rstrip(",.!?;:")
        if not verb or len(verb) < 4:
            return False

        # Get the ending
        if verb.endswith("ите"):
            ending = "ите"
        elif verb.endswith("ете"):
            ending = "ете"
        else:
            return False  # Shouldn't happen based on pattern

        try:
            # Parse the verb
            parses = morphology.parse(verb)
            if not parses:
                return False

            # Check all parses to understand what this word CAN be
            has_imperative = False
            has_indicative = False  # Present or future tense

            for parse in parses:
                if not hasattr(parse, "tag"):
                    continue

                tag = parse.tag
                pos = getattr(tag, "POS", None)

                # Only check verbs
                if pos not in ("VERB", "INFN"):
                    continue

                mood = getattr(tag, "mood", None)

                if mood == "impr":  # Imperative
                    has_imperative = True
                elif mood == "indc":  # Indicative (present/future)
                    has_indicative = True

            # If the verb can ONLY be one form (not ambiguous), it's NOT an error
            # Example: "предоставляете" can ONLY be indicative (present), not imperative
            if has_indicative and not has_imperative:
                return False  # Only indicative = correct -ете form
            if has_imperative and not has_indicative:
                return False  # Only imperative = correct -ите form

            # If it's ambiguous (can be both), check context
            if has_imperative and has_indicative:
                # Look for imperative markers in context
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 100)
                context = text[context_start:context_end].lower()

                # Imperative markers
                imperative_markers = [
                    "пожалуйста",
                    "please",
                    "!",  # Exclamation mark often indicates command
                    "прошу",
                    "просьба",  # I ask, request
                    "давайте",  # Let's
                ]

                has_imperative_context = any(marker in context for marker in imperative_markers)

                # Indicative markers (future/present)
                indicative_markers = [
                    "вы ",  # You (formal/plural)
                    "когда",  # When (future)
                    "если",  # If (conditional)
                ]

                has_indicative_context = any(marker in context for marker in indicative_markers)

                # If context is clear, check if form matches context
                if has_imperative_context and ending == "ете":
                    # Context suggests imperative but uses -ете - ERROR!
                    return True
                elif has_indicative_context and ending == "ите":
                    # Context suggests indicative but uses -ите - ERROR!
                    return True

            # Default: no error (we're conservative to avoid false positives)
            return False

        except Exception as e:
            import logging

            logging.debug(f"Error checking imperative vs future for '{verb}': {e}")
            return False  # On error, don't report

    def _check_particle_taki(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        morphology: Any,
    ) -> bool:
        """Check if this is actually the particle ТАКИ, not adjective forms like таких.

        Returns True if it's an error (needs hyphen), False otherwise.

        Problem: Pattern matches "таки" + letters, which catches:
        - "таки" (particle) - should have hyphen: пришёл-таки
        - "таких" (adjective genitive plural) - NO hyphen needed
        - "такие" (adjective nominative plural) - NO hyphen needed
        """
        # Get the full matched word
        word = match.group(0).strip().lower()

        # Fixed particle forms that need hyphen
        particle_forms = {
            "всё-таки",
            "все-таки",
            "так-таки",
            "всётаки",
            "всетаки",
            "тактаки",  # Wrong forms without hyphen
        }

        # Check if it's one of the fixed forms
        if word in particle_forms:
            # Check if it has hyphen
            return "-" not in word  # Error if no hyphen

        # For other words starting with "таки", check if it's adjective
        if word.startswith("таки"):
            try:
                parses = morphology.parse(word)
                if not parses:
                    return False  # Unknown word, don't flag

                # Check if ANY parse is adjective (такой/такая/такое/такие/таких)
                for parse in parses:
                    if not hasattr(parse, "tag"):
                        continue

                    tag = parse.tag
                    pos = getattr(tag, "POS", None)

                    # If it's an adjective (ADJF) or pronoun-adjective (APRO)
                    if pos in ("ADJF", "APRO"):
                        # Check if lemma is "такой" (such)
                        lemma = getattr(parse, "normal_form", "").lower()
                        if lemma == "такой":
                            return False  # It's the adjective "такой", not particle "таки"

            except Exception as e:
                import logging

                logging.debug(f"Error checking particle таки for '{word}': {e}")
                return False

        # If we get here, assume it's not a common false positive
        # But to be safe, only flag if it matches very specific patterns
        return False  # Be conservative to avoid false positives

    def _check_comma_before_conjunction(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        text: str,
    ) -> bool:
        """Check if comma is needed before subordinate conjunction.

        Returns True if it's an error (missing comma), False if correct.

        Problem: Rule flags conjunctions at sentence start where no comma is needed.
        Examples:
        - "Если вы хотите" (sentence start) - NO comma needed
        - "пришёл, чтобы помочь" (mid-sentence) - comma needed
        """
        # Get position of the matched conjunction
        match_start = match.start()

        # Look back to find sentence start
        # Check if conjunction is near beginning of sentence
        # Look for: newline, period, question mark, exclamation, or start of text
        text_before = text[:match_start]

        # Find last sentence boundary
        sentence_markers = ["\n\n", "\n#", ". ", "! ", "? "]
        last_boundary = 0

        for marker in sentence_markers:
            pos = text_before.rfind(marker)
            if pos > last_boundary:
                last_boundary = pos + len(marker)

        # Get text from last boundary to conjunction
        text_since_boundary = text_before[last_boundary:].strip()

        # Check for markdown/formatting that indicates sentence start
        # - Headings: ###, ##, #
        # - Lists: -, *, 1., 2., etc.
        # - Bold/emphasis: **, __, *, _
        # - Blockquote: >
        if text_since_boundary.startswith(("#", "-", "*", ">", "1.", "2.", "3.", "4.", "5.")):
            return False  # After heading/list marker, no comma needed

        # If there's very little text before conjunction (< 15 chars)
        # it's probably at sentence start - no comma needed
        if len(text_since_boundary) < 15:
            return False  # Not an error - conjunction at sentence start

        # Check if there's already a comma before the conjunction
        # Look at characters immediately before the match
        chars_before = text_before[-10:].strip() if len(text_before) >= 10 else text_before.strip()

        if chars_before.endswith(","):
            return False  # Comma already present, not an error

        # Check for markdown bold/emphasis markers just before
        # Example: "**Примечание**: Если..." - no comma needed
        if any(chars_before.endswith(marker) for marker in ["**:", "__:", "*:", "_:", ":"]):
            return False  # After bold text with colon, no comma needed

        # If we get here, conjunction is mid-sentence without comma
        # This SHOULD have a comma
        return True  # Error - missing comma before conjunction

    def _check_i_y_after_prefix(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
    ) -> bool:
        """Check I/Y after Russian prefix ending in consonant.

        Returns True if it's an error (wrong vowel), False if correct.

        Russian rule:
        - After Russian prefixes on consonant: И → Ы (разыскать, подыграть)
        - After меж-, сверх-: keep И (межинститутский)
        - After foreign prefixes (super-, trans-, etc.): keep И
        - Foreign words (Greek, Latin): keep original spelling

        Problem: Pattern catches foreign words like "синтаксис" (Greek σύνταξις)
        """
        groups = match.groups()
        if len(groups) < 3:
            return False

        prefix = groups[0].lower()  # раз, без, из, с, под, etc.
        vowel = groups[1].lower()  # и or ы
        rest = groups[2]  # rest of word

        full_word = (prefix + vowel + rest).lower()

        # Foreign loanwords that should NOT change И→Ы
        # Greek, Latin, and other foreign words that happen to start with
        # what looks like a Russian prefix
        foreign_loanwords = {
            # Greek words (starting with "син-" = σύν = together)
            "синтаксис",
            "синтез",
            "синоним",
            "синус",
            "синагога",
            "синхронный",
            "синхронизация",
            "синкретизм",
            "синопсис",
            # Latin/international words
            "символ",
            "симметрия",
            "симпозиум",
            "симптом",
            "симуляция",
            "симулятор",
            "симфония",
            "силуэт",
            "сизиф",
            # Words with prefix "с-" that are foreign
            "сигнал",
            "сигнатура",
            "систола",
            "ситуация",
            "сигара",
            # Other foreign words that might match patterns
            "изолят",
            "изомер",  # iso- (Greek)
        }

        if full_word in foreign_loanwords:
            return False  # Foreign word, keep original spelling

        # Words with foreign prefixes (keep И)
        foreign_prefix_words = {
            "межинститутский",
            "межигровой",  # меж-
            "сверхинтересный",
            "сверхинтеллектуальный",  # сверх-
            "постимпрессионизм",
            "постиндустриальный",  # пост-
        }

        if full_word in foreign_prefix_words:
            return False  # Foreign prefix, keep И

        # If word has И after Russian prefix on consonant, should be Ы
        # But we're being conservative - only flag clear errors
        # For now, return False to avoid false positives
        # Real implementation would check if word is in Russian dictionary
        return False  # Conservative: don't flag

    def _check_comparative_kak(
        self,
        match: re.Match[str],
        pattern_config: dict[str, Any],
        text: str,
    ) -> bool:
        r"""Check if КАК needs comma (comparative construction).

        Returns True if it's an error (missing comma), False if correct.

        Problem: Pattern `\s+(как)\s+` catches:
        - Real comparatives: "белый как снег" → needs comma: "белый, как снег"
        - Markdown headings: "## Как участвовать" → NO comma needed
        - Fixed expressions: "как можно", "как всегда" → NO comma needed
        """
        # Get position and context
        match_start = match.start()

        # Check if this is a markdown heading
        # Look back to start of line
        line_start = text.rfind("\n", 0, match_start)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1  # Move past newline

        # Get text from line start to match
        text_before_kak = text[line_start:match_start]

        # If line starts with # (markdown heading), skip
        if text_before_kak.strip().startswith("#"):
            return False  # Markdown heading, no comma needed

        # Check for fixed expressions
        # Look at word after "как"
        match_end = match.end()
        words_after = text[match_end : match_end + 50].split()
        if words_after:
            first_word_after = words_after[0].strip(",.!?;:")
            fixed_expressions = {
                "можно",
                "всегда",
                "нельзя",
                "правило",
                "обычно",
                "только",
                "раз",
                "будто",
                "если",
            }
            if first_word_after.lower() in fixed_expressions:
                return False  # Fixed expression, no comma

        # Check if comma is already present
        chars_before = text[max(0, match_start - 5) : match_start]
        if "," in chars_before:
            return False  # Comma already there

        # For now, be conservative - don't flag
        # Real implementation would check if it's truly comparative
        return False  # Conservative: don't flag

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
