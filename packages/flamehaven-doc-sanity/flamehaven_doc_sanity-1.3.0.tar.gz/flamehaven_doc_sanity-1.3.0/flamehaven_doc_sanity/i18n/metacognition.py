"""MetaCognition layer for translation quality validation.

Inspired by DFI-META's meta-cognitive evolution system, this module provides
self-reflective quality assessment for translations.

Components:
- TranslationQualityOracle: Self-evaluates translation quality
- ConsistencyChecker: Ensures terminology consistency
- ContextAnalyzer: Understands technical vs casual context
"""

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class TranslationQualityTensor:
    """Meta-cognitive tensor for translation quality assessment.

    Inspired by DFI-META's MetaCognitiveTensor.
    """

    semantic_fidelity: float = 0.0  # Meaning preserved
    technical_accuracy: float = 0.0  # Technical terms correct
    fluency: float = 0.0  # Natural English flow
    consistency: float = 0.0  # Term usage consistent
    context_awareness: float = 0.0  # Appropriate for context

    def compute_omega(self) -> float:
        """Calculate overall translation quality omega score.

        Weights based on translation priorities:
        - Semantic fidelity most important (30%)
        - Technical accuracy critical (25%)
        - Fluency important (20%)
        - Consistency matters (15%)
        - Context awareness nice-to-have (10%)
        """
        weights = {
            "semantic_fidelity": 0.30,
            "technical_accuracy": 0.25,
            "fluency": 0.20,
            "consistency": 0.15,
            "context_awareness": 0.10,
        }

        return sum(getattr(self, k) * v for k, v in weights.items())


@dataclass
class QualityAssessment:
    """Result of translation quality assessment."""

    omega_score: float  # Overall quality (0.0 to 1.0)
    tensor: TranslationQualityTensor
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    should_retranslate: bool = False
    confidence: float = 0.0


class TranslationQualityOracle:
    """Self-evaluates translation quality using meta-cognitive analysis.

    Acts as the "Oracle" in the translation tribunal, providing
    objective quality assessment without human intervention.
    """

    def __init__(self, strict_threshold: float = 0.85):
        """Initialize quality oracle.

        Args:
            strict_threshold: Omega threshold for acceptable quality
        """
        self.strict_threshold = strict_threshold
        self.evaluation_history = []

    def evaluate(
        self,
        original: str,
        translated: str,
        source_lang: str,
        preserved_terms: List[str] = None,
    ) -> QualityAssessment:
        """Evaluate translation quality using meta-cognitive analysis.

        Args:
            original: Original text
            translated: Translated text
            source_lang: Source language code
            preserved_terms: Terms that should be preserved

        Returns:
            QualityAssessment with detailed analysis
        """
        preserved_terms = preserved_terms or []

        # Initialize tensor
        tensor = TranslationQualityTensor()

        # Evaluate semantic fidelity
        tensor.semantic_fidelity = self._evaluate_semantic_fidelity(
            original, translated
        )

        # Evaluate technical accuracy
        tensor.technical_accuracy = self._evaluate_technical_accuracy(
            translated, preserved_terms
        )

        # Evaluate fluency
        tensor.fluency = self._evaluate_fluency(translated)

        # Consistency evaluated externally (needs multiple translations)
        # For very short translations, consistency is questionable
        if len(translated) < 5:
            tensor.consistency = 0.3
        else:
            tensor.consistency = 0.8  # Default assumption

        # Evaluate context awareness
        tensor.context_awareness = self._evaluate_context(original, translated)

        # Compute omega
        omega = tensor.compute_omega()

        # Generate issues and recommendations
        issues = []
        recommendations = []

        if tensor.semantic_fidelity < 0.7:
            issues.append("Semantic meaning may be lost in translation")
            recommendations.append("Consider rephrasing or adding clarification")

        if tensor.technical_accuracy < 0.8:
            issues.append("Technical terms may not be preserved correctly")
            recommendations.append("Review technical terminology")

        if tensor.fluency < 0.6:
            issues.append("Translation lacks natural English flow")
            recommendations.append("Rewrite for better readability")

        # Determine if retranslation needed
        should_retranslate = omega < self.strict_threshold

        # Record evaluation
        self.evaluation_history.append(
            {"omega": omega, "tensor": tensor, "issues_count": len(issues)}
        )

        return QualityAssessment(
            omega_score=omega,
            tensor=tensor,
            issues=issues,
            recommendations=recommendations,
            should_retranslate=should_retranslate,
            confidence=min(1.0, omega * 1.1),  # Confidence based on omega
        )

    def _evaluate_semantic_fidelity(self, original: str, translated: str) -> float:
        """Evaluate if semantic meaning is preserved.

        Uses heuristics:
        - Length ratio (translations shouldn't be too different in length)
        - Keyword preservation
        - Structural similarity
        """
        if not original or not translated:
            return 0.0

        # Length ratio check (good translations are usually similar length)
        len_ratio = min(len(original), len(translated)) / max(
            len(original), len(translated)
        )

        # Extract "important" words (longer words, likely keywords)
        original_keywords = set(w for w in original.split() if len(w) > 3)
        translated_keywords = set(w for w in translated.split() if len(w) > 3)

        # Check keyword overlap (some should remain)
        if original_keywords:
            overlap = len(original_keywords & translated_keywords) / len(
                original_keywords
            )
        else:
            overlap = 0.5

        # Structural similarity (punctuation patterns)
        orig_punct = set(c for c in original if c in ".,!?;:")
        trans_punct = set(c for c in translated if c in ".,!?;:")
        punct_similarity = len(orig_punct & trans_punct) / max(
            1, len(orig_punct | trans_punct)
        )

        # Combine scores
        fidelity = len_ratio * 0.4 + overlap * 0.4 + punct_similarity * 0.2

        return min(1.0, fidelity)

    def _evaluate_technical_accuracy(
        self, translated: str, preserved_terms: List[str]
    ) -> float:
        """Evaluate if technical terms are preserved correctly."""
        # Penalize extremely short translations
        if len(translated) < 3:
            return 0.1  # Almost certainly lost all technical content

        if not preserved_terms:
            # Default score depends on translation quality
            # Short translations unlikely to be technically accurate
            if len(translated.split()) < 3:
                return 0.3
            return 0.9  # No terms to preserve, assume OK

        # Check how many preserved terms appear in translation
        found = sum(1 for term in preserved_terms if term in translated)

        accuracy = found / len(preserved_terms)

        # Check for common technical translation errors
        errors = 0

        # CamelCase broken into words
        if re.search(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", translated):
            errors += 1

        # snake_case broken
        if re.search(r"\b[a-z]+\s+[a-z]+\b", translated) and "_" not in translated:
            errors += 1

        # Penalize for errors
        accuracy -= errors * 0.1

        return max(0.0, min(1.0, accuracy))

    def _evaluate_fluency(self, translated: str) -> float:
        """Evaluate if translation is fluent English.

        Checks:
        - Sentence structure
        - Common English patterns
        - Grammar-like heuristics
        """
        if not translated:
            return 0.0

        # Extremely short translations are not fluent
        if len(translated) < 3:
            return 0.1

        fluency = 1.0

        # Check for common non-fluency indicators
        # Repeated words
        words = translated.lower().split()
        if len(words) != len(set(words)):
            fluency -= 0.1

        # Very short or very long sentences
        if len(words) == 1:
            fluency -= 0.5  # Single word is rarely fluent
        elif len(words) < 3:
            fluency -= 0.3  # Very short
        elif len(words) > 50:
            fluency -= 0.1

        # Check for proper capitalization
        if translated and not translated[0].isupper():
            fluency -= 0.1

        # Check for sentence endings
        if not translated.rstrip().endswith((".", "!", "?", ":")):
            fluency -= 0.05

        # Bonus for common English patterns
        if re.search(
            r"\b(the|a|an|is|are|was|were|have|has|will|would|can|could)\b",
            translated.lower(),
        ):
            fluency += 0.1

        return max(0.0, min(1.0, fluency))

    def _evaluate_context(self, original: str, translated: str) -> float:
        """Evaluate if translation is appropriate for context (code comment).

        Technical comments should be:
        - Concise
        - Clear
        - Professional
        - Code-aware
        """
        context_score = 0.8  # Default

        # Concise check (comments shouldn't be too long)
        if len(translated.split()) > 30:
            context_score -= 0.2

        # Professional tone (avoid casual language in translation)
        casual_indicators = ["lol", "btw", "omg", "gonna", "wanna"]
        if any(word in translated.lower() for word in casual_indicators):
            context_score -= 0.3

        # Code-aware (should contain some technical terms)
        if re.search(
            r"\b(function|method|class|variable|parameter|return|error)\b",
            translated.lower(),
        ):
            context_score += 0.1

        return max(0.0, min(1.0, context_score))


class ConsistencyChecker:
    """Ensures terminology consistency across translations.

    Tracks term translations and ensures they remain consistent
    throughout the codebase.
    """

    def __init__(self):
        """Initialize consistency checker."""
        self.term_map = {}  # Maps original terms to their translations
        self.violations = []

    def register_translation(self, original: str, translated: str):
        """Register a term translation for consistency checking.

        Args:
            original: Original term
            translated: Translated term
        """
        # Extract key terms from both
        original_terms = self._extract_terms(original)
        translated_terms = self._extract_terms(translated)

        # Map terms (simplified: just store pairs)
        for orig_term in original_terms:
            if orig_term not in self.term_map:
                self.term_map[orig_term] = set()

            # Add all translated terms as possible translations
            self.term_map[orig_term].update(translated_terms)

    def check_consistency(
        self, original: str, translated: str
    ) -> Tuple[bool, List[str]]:
        """Check if translation is consistent with previous translations.

        Args:
            original: Original text
            translated: Translated text

        Returns:
            (is_consistent, list_of_violations)
        """
        original_terms = self._extract_terms(original)
        translated_terms = self._extract_terms(translated)

        violations = []

        for orig_term in original_terms:
            if orig_term in self.term_map:
                # Check if translated term matches previous translations
                expected_translations = self.term_map[orig_term]

                # Check if any translated term matches
                found = any(t in expected_translations for t in translated_terms)

                if not found and expected_translations:
                    violations.append(
                        f"Term '{orig_term}' translated differently than before. "
                        f"Expected one of: {expected_translations}"
                    )

        is_consistent = len(violations) == 0

        return is_consistent, violations

    def _extract_terms(self, text: str) -> List[str]:
        """Extract key terms from text.

        Focuses on:
        - CamelCase words
        - snake_case words
        - UPPER_CASE words
        - Technical keywords
        """
        terms = []

        # CamelCase
        terms.extend(re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", text))

        # snake_case
        terms.extend(re.findall(r"\b[a-z]+_[a-z_]+\b", text))

        # UPPER_CASE
        terms.extend(re.findall(r"\b[A-Z][A-Z_]+\b", text))

        # Common technical words (3+ chars)
        words = text.split()
        for word in words:
            clean = word.strip(".,!?;:()[]{}")
            if len(clean) >= 3 and clean[0].isupper():
                terms.append(clean)

        return list(set(terms))  # Unique terms

    def get_consistency_score(self) -> float:
        """Get overall consistency score.

        Returns:
            Score from 0.0 to 1.0
        """
        if not self.term_map:
            return 1.0  # No inconsistencies if no terms tracked

        total_terms = len(self.term_map)
        consistent_terms = sum(
            1
            for terms in self.term_map.values()
            if len(terms) == 1  # Only one translation ever used
        )

        return consistent_terms / total_terms if total_terms > 0 else 1.0


class ContextAnalyzer:
    """Analyzes context to determine appropriate translation style.

    Different contexts require different translation approaches:
    - Code comments: Concise, technical
    - Docstrings: Detailed, professional
    - README: Engaging, clear
    - Error messages: Precise, actionable
    """

    CONTEXT_TYPES = {
        "code_comment": {
            "style": "concise",
            "tone": "technical",
            "max_length_multiplier": 1.2,
        },
        "docstring": {
            "style": "detailed",
            "tone": "professional",
            "max_length_multiplier": 1.5,
        },
        "readme": {
            "style": "engaging",
            "tone": "clear",
            "max_length_multiplier": 2.0,
        },
        "error_message": {
            "style": "precise",
            "tone": "actionable",
            "max_length_multiplier": 1.0,
        },
    }

    def analyze_context(self, text: str, node_type: str = None) -> Dict[str, any]:
        """Analyze context to determine translation requirements.

        Args:
            text: Text to analyze
            node_type: Type of node (from CodeCommentParser)

        Returns:
            Dict with context analysis
        """
        # Determine context type
        if node_type == "inline_comment":
            context_type = "code_comment"
        elif node_type == "docstring":
            context_type = "docstring"
        elif "error" in text.lower() or "exception" in text.lower():
            context_type = "error_message"
        else:
            context_type = "code_comment"  # Default

        context_spec = self.CONTEXT_TYPES.get(
            context_type, self.CONTEXT_TYPES["code_comment"]
        )

        # Analyze text characteristics
        word_count = len(text.split())
        has_code_terms = bool(re.search(r"[A-Z][a-z]+[A-Z]|[a-z]+_[a-z]+", text))
        has_technical_words = bool(
            re.search(
                r"\b(function|class|method|parameter|return|variable|error|exception)\b",
                text.lower(),
            )
        )

        return {
            "context_type": context_type,
            "style": context_spec["style"],
            "tone": context_spec["tone"],
            "max_length": int(word_count * context_spec["max_length_multiplier"]),
            "has_code_terms": has_code_terms,
            "has_technical_words": has_technical_words,
            "recommended_approach": self._recommend_approach(
                context_spec, has_technical_words
            ),
        }

    def _recommend_approach(self, context_spec: Dict, has_technical: bool) -> str:
        """Recommend translation approach based on context."""
        if has_technical and context_spec["style"] == "concise":
            return "preserve_technical_terms_minimize_prose"
        elif context_spec["style"] == "detailed":
            return "full_translation_with_examples"
        elif context_spec["style"] == "engaging":
            return "natural_flowing_translation"
        else:
            return "literal_technical_translation"
