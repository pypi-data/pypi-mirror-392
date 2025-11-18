"""Language detection with confidence scoring.

Detects source language in code comments, docstrings, and documentation
with high accuracy and confidence metrics.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""

    language: str  # ISO 639-1 code (ko, ja, zh, es, etc.)
    confidence: float  # 0.0 to 1.0
    script: str  # latin, hangul, kanji, hanzi, etc.
    samples: List[str]  # Sample texts that led to detection


class LanguageDetector:
    """Detects language in text with confidence scoring.

    Uses character-based heuristics and pattern matching.
    Optimized for code comments and technical documentation.
    """

    # Character range patterns for different scripts
    SCRIPT_PATTERNS = {
        "hangul": r"[\uAC00-\uD7AF]",  # Korean
        "hiragana": r"[\u3040-\u309F]",  # Japanese
        "katakana": r"[\u30A0-\u30FF]",  # Japanese
        "kanji": r"[\u4E00-\u9FFF]",  # Japanese/Chinese
        "hanzi": r"[\u4E00-\u9FFF]",  # Chinese (same as kanji)
        "cyrillic": r"[\u0400-\u04FF]",  # Russian, etc.
        "arabic": r"[\u0600-\u06FF]",  # Arabic
        "thai": r"[\u0E00-\u0E7F]",  # Thai
        "latin": r"[A-Za-z]",  # English, European
    }

    # Common words/particles for language identification
    LANGUAGE_MARKERS = {
        "en": [
            "the",
            "is",
            "are",
            "be",
            "this",
            "that",
            "with",
            "from",
            "have",
            "has",
            "will",
            "would",
            "can",
            "could",
            "should",
            "and",
            "or",
            "but",
            "if",
            "when",
        ],
        "ko": [
            "입니다",
            "합니다",
            "있습니다",
            "하다",
            "되다",
            "이다",
            "을",
            "를",
            "이",
            "가",
            "은",
            "는",
        ],
        "ja": ["です", "ます", "する", "ある", "いる", "の", "を", "が", "は", "に"],
        "zh": ["的", "是", "了", "在", "有", "我", "你", "他", "这", "那"],
        "es": ["el", "la", "de", "que", "y", "en", "un", "ser", "estar"],
        "fr": ["le", "de", "un", "être", "et", "à", "avoir", "que"],
        "de": ["der", "die", "das", "und", "in", "von", "zu", "den"],
        "ru": ["и", "в", "не", "на", "я", "быть", "с", "он"],
    }

    def __init__(self):
        """Initialize language detector."""
        self.detection_cache = {}

    def detect(self, text: str, context: str = None) -> LanguageDetectionResult:
        """Detect language in text.

        Args:
            text: Text to analyze
            context: Optional context hint (e.g., 'code_comment', 'docstring')

        Returns:
            LanguageDetectionResult with detected language and confidence
        """
        if not text or not text.strip():
            return LanguageDetectionResult(
                language="en", confidence=0.0, script="latin", samples=[]
            )

        # Clean text for analysis
        clean_text = self._clean_text(text)

        # Detect script
        script, script_confidence = self._detect_script(clean_text)

        # Detect language based on script and markers
        language, lang_confidence = self._detect_language(clean_text, script)

        # Extract sample phrases
        samples = self._extract_samples(text, language)

        # Combine confidences
        final_confidence = (script_confidence + lang_confidence) / 2

        return LanguageDetectionResult(
            language=language,
            confidence=final_confidence,
            script=script,
            samples=samples[:3],  # Top 3 samples
        )

    def _clean_text(self, text: str) -> str:
        """Clean text for analysis."""
        # Remove URLs
        text = re.sub(r"https?://\S+", "", text)

        # Remove code-like patterns
        text = re.sub(r"[a-zA-Z_][a-zA-Z0-9_]*\(", "", text)  # function calls
        text = re.sub(r"\b[A-Z_][A-Z0-9_]+\b", "", text)  # CONSTANTS

        # Remove numbers
        text = re.sub(r"\d+", "", text)

        return text.strip()

    def _detect_script(self, text: str) -> tuple[str, float]:
        """Detect writing script.

        Returns:
            (script_name, confidence)
        """
        if not text:
            return "latin", 0.0

        script_scores = {}

        for script, pattern in self.SCRIPT_PATTERNS.items():
            matches = len(re.findall(pattern, text))
            if matches > 0:
                # Confidence based on character ratio
                script_scores[script] = matches / len(text)

        if not script_scores:
            return "latin", 0.5

        # Get dominant script
        dominant = max(script_scores.items(), key=lambda x: x[1])

        return dominant[0], min(1.0, dominant[1] * 2)

    def _detect_language(self, text: str, script: str) -> tuple[str, float]:
        """Detect language based on script and markers.

        Returns:
            (language_code, confidence)
        """
        # Script to likely languages mapping
        script_to_langs = {
            "hangul": ["ko"],
            "hiragana": ["ja"],
            "katakana": ["ja"],
            "kanji": ["ja", "zh"],
            "hanzi": ["zh"],
            "cyrillic": ["ru"],
            "arabic": ["ar"],
            "thai": ["th"],
            "latin": ["en", "es", "fr", "de", "pt", "it"],
        }

        candidate_langs = script_to_langs.get(script, ["en"])

        # Check for language markers
        text_lower = text.lower()
        lang_scores = {}

        for lang in candidate_langs:
            if lang in self.LANGUAGE_MARKERS:
                markers = self.LANGUAGE_MARKERS[lang]
                # Use word boundary matching for latin script languages to avoid false positives
                if script == "latin":
                    words = set(text_lower.split())
                    score = sum(1 for marker in markers if marker in words)
                else:
                    # Use substring matching for non-latin scripts
                    score = sum(1 for marker in markers if marker in text_lower)
                if score > 0:
                    lang_scores[lang] = score / len(markers)

        if lang_scores:
            best_lang = max(lang_scores.items(), key=lambda x: x[1])
            return best_lang[0], min(1.0, best_lang[1] * 3)

        # Default to first candidate
        return candidate_langs[0], 0.6 if script != "latin" else 0.3

    def _extract_samples(self, text: str, language: str) -> List[str]:
        """Extract sample phrases in detected language."""
        # Split into sentences/phrases
        sentences = re.split(r"[.!?。！？\n]+", text)

        samples = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Meaningful length
                # Check if contains target language characters
                if language in self.LANGUAGE_MARKERS:
                    markers = self.LANGUAGE_MARKERS[language]
                    if any(marker in sentence.lower() for marker in markers):
                        samples.append(sentence)

        return samples[:5]  # Top 5

    def detect_batch(self, texts: List[str]) -> Dict[str, LanguageDetectionResult]:
        """Detect language for multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            Dict mapping text to detection result
        """
        results = {}
        for text in texts:
            results[text] = self.detect(text)
        return results

    def is_english(self, text: str, threshold: float = 0.7) -> bool:
        """Quick check if text is English.

        Uses optimized heuristics for fast English detection.

        Args:
            text: Text to check
            threshold: Confidence threshold for English detection

        Returns:
            True if confidently English
        """
        # Quick check: if contains non-latin characters, it's not English
        if any("\uac00" <= c <= "\ud7af" for c in text):  # Korean
            return False
        if any(
            "\u3040" <= c <= "\u309f" or "\u30a0" <= c <= "\u30ff" for c in text
        ):  # Japanese
            return False
        if any("\u0400" <= c <= "\u04ff" for c in text):  # Cyrillic
            return False

        # Check for common English words
        words = set(text.lower().split())
        english_markers = {
            "the",
            "is",
            "are",
            "this",
            "that",
            "with",
            "and",
            "or",
            "but",
        }

        # If we find 2+ English markers, it's likely English
        matches = sum(1 for marker in english_markers if marker in words)
        if matches >= 2:
            return True

        # Fallback to full detection for edge cases
        result = self.detect(text)
        return result.language == "en" and result.confidence >= threshold
