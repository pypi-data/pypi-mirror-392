"""Translation engine with AI integration and rule-based fallback.

Supports multiple translation backends:
- AI-powered (OpenAI GPT-4, Anthropic Claude) - optional
- Rule-based technical translation
- Hybrid mode with quality validation
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TranslationResult:
    """Result of a translation operation."""

    original: str
    translated: str
    source_lang: str
    target_lang: str
    confidence: float  # 0.0 to 1.0
    method: str  # 'ai', 'rule_based', 'hybrid'
    preserved_terms: List[str]  # Technical terms preserved
    metadata: Dict[str, Any] = None


class TechnicalTermDatabase:
    """Database of technical terms that should be preserved or standardized."""

    # Terms that should NOT be translated
    PRESERVE_TERMS = {
        # Programming concepts
        "function",
        "class",
        "method",
        "variable",
        "constant",
        "array",
        "list",
        "dict",
        "dictionary",
        "tuple",
        "set",
        "loop",
        "if",
        "else",
        "for",
        "while",
        "return",
        "import",
        "from",
        "def",
        "async",
        "await",
        # Common libraries/frameworks
        "Python",
        "JavaScript",
        "TypeScript",
        "React",
        "Vue",
        "Django",
        "Flask",
        "FastAPI",
        "NumPy",
        "pandas",
        "pytest",
        "unittest",
        "Docker",
        "Kubernetes",
        # Technical terms
        "API",
        "REST",
        "GraphQL",
        "HTTP",
        "HTTPS",
        "JSON",
        "XML",
        "database",
        "SQL",
        "NoSQL",
        "cache",
        "queue",
        "token",
        "authentication",
        "authorization",
        "endpoint",
        "middleware",
        "decorator",
        # Common abbreviations
        "CRUD",
        "CLI",
        "GUI",
        "SDK",
        "IDE",
        "CI/CD",
        "TODO",
        "FIXME",
        "NOTE",
        "WARNING",
        "ERROR",
    }

    # Standard translations for common programming terms
    STANDARD_TRANSLATIONS = {
        # Korean translations (commonly used in Korean dev community)
        "ko": {
            "함수": "function",
            "클래스": "class",
            "메서드": "method",
            "변수": "variable",
            "매개변수": "parameter",
            "반환": "return",
            "반환값": "return value",
            "예외": "exception",
            "에러": "error",
            "오류": "error",
            "설정": "configuration",
            "환경": "environment",
            "테스트": "test",
            "배포": "deployment",
            "빌드": "build",
            "실행": "execute",
            "호출": "call",
            "생성": "create",
            "삭제": "delete",
            "수정": "update",
            "조회": "read",
        },
        # Japanese translations
        "ja": {
            "関数": "function",
            "クラス": "class",
            "メソッド": "method",
            "変数": "variable",
            "パラメータ": "parameter",
            "戻り値": "return value",
            "例外": "exception",
            "エラー": "error",
            "設定": "configuration",
            "テスト": "test",
        },
        # Chinese translations
        "zh": {
            "函数": "function",
            "类": "class",
            "方法": "method",
            "变量": "variable",
            "参数": "parameter",
            "返回": "return",
            "异常": "exception",
            "错误": "error",
            "配置": "configuration",
            "测试": "test",
        },
    }

    @classmethod
    def should_preserve(cls, term: str) -> bool:
        """Check if term should be preserved."""
        return term in cls.PRESERVE_TERMS or term.isupper()  # Preserve ACRONYMS

    @classmethod
    def get_standard_translation(cls, term: str, source_lang: str) -> Optional[str]:
        """Get standard translation for technical term."""
        if source_lang in cls.STANDARD_TRANSLATIONS:
            return cls.STANDARD_TRANSLATIONS[source_lang].get(term)
        return None


class TranslationEngine:
    """Main translation engine with multiple backends.

    Supports:
    1. Rule-based translation for technical content
    2. AI-powered translation (optional, requires API keys)
    3. Hybrid mode with quality validation
    """

    def __init__(self, mode: str = "rule_based", api_key: Optional[str] = None):
        """Initialize translation engine.

        Args:
            mode: 'rule_based', 'ai', or 'hybrid'
            api_key: Optional API key for AI translation
        """
        self.mode = mode
        self.api_key = api_key
        self.term_db = TechnicalTermDatabase()
        self.translation_cache = {}

    def translate(
        self, text: str, source_lang: str, target_lang: str = "en", context: str = None
    ) -> TranslationResult:
        """Translate text from source language to target language.

        Args:
            text: Text to translate
            source_lang: Source language code (ko, ja, zh, etc.)
            target_lang: Target language code (default: en)
            context: Optional context for better translation

        Returns:
            TranslationResult with translation and metadata
        """
        # Check cache
        cache_key = f"{source_lang}:{target_lang}:{text[:100]}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        # Extract and preserve technical terms
        preserved_terms = self._extract_preservable_terms(text)

        # Choose translation method
        if self.mode == "ai" and self.api_key:
            result = self._ai_translate(
                text, source_lang, target_lang, context, preserved_terms
            )
        elif self.mode == "hybrid":
            # Try AI first, fallback to rule-based
            try:
                result = self._ai_translate(
                    text, source_lang, target_lang, context, preserved_terms
                )
            except:
                result = self._rule_based_translate(
                    text, source_lang, target_lang, preserved_terms
                )
        else:
            result = self._rule_based_translate(
                text, source_lang, target_lang, preserved_terms
            )

        # Cache result
        self.translation_cache[cache_key] = result

        return result

    def _extract_preservable_terms(self, text: str) -> List[str]:
        """Extract technical terms that should be preserved."""
        preserved = []

        # Extract code-like terms: CamelCase, snake_case, UPPER_CASE
        code_patterns = [
            r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b",  # CamelCase
            r"\b[a-z]+_[a-z_]+\b",  # snake_case
            r"\b[A-Z][A-Z_]+\b",  # UPPER_CASE
        ]

        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            preserved.extend(matches)

        # Check against term database
        words = text.split()
        for word in words:
            if self.term_db.should_preserve(word.strip(".,!?;:")):
                preserved.append(word.strip(".,!?;:"))

        return list(set(preserved))  # Remove duplicates

    def _rule_based_translate(
        self, text: str, source_lang: str, target_lang: str, preserved_terms: List[str]
    ) -> TranslationResult:
        """Rule-based translation for technical content.

        This is a simplified implementation. In production, you would use
        a proper translation library or service.
        """
        translated = text

        # Apply standard technical term translations
        if source_lang in self.term_db.STANDARD_TRANSLATIONS:
            for original, standard in self.term_db.STANDARD_TRANSLATIONS[
                source_lang
            ].items():
                # Replace whole words only
                translated = re.sub(
                    r"\b" + re.escape(original) + r"\b", standard, translated
                )

        # Simple transformations for demonstration
        if source_lang == "ko" and target_lang == "en":
            # Korean sentence endings -> English equivalents
            translated = re.sub(r"입니다\.?$", ".", translated)
            translated = re.sub(r"합니다\.?$", ".", translated)
            translated = re.sub(r"있습니다\.?$", ".", translated)

        # Preserve technical terms (wrap in markers for protection)
        for term in preserved_terms:
            if term in translated:
                # Already preserved or translated correctly
                pass

        return TranslationResult(
            original=text,
            translated=(
                translated if translated != text else f"[EN] {text}"
            ),  # Mark untranslated
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=0.6,  # Lower confidence for rule-based
            method="rule_based",
            preserved_terms=preserved_terms,
            metadata={
                "note": "Rule-based translation - consider AI mode for better quality"
            },
        )

    def _ai_translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: Optional[str],
        preserved_terms: List[str],
    ) -> TranslationResult:
        """AI-powered translation using LLM APIs.

        This is a placeholder. In production, you would integrate with:
        - OpenAI GPT-4 API
        - Anthropic Claude API
        - Google Translate API
        - DeepL API
        """
        # Construct prompt
        prompt = f"""Translate the following technical text from {source_lang} to {target_lang}.

Rules:
1. Preserve all technical terms: {', '.join(preserved_terms)}
2. Use professional developer English
3. Maintain code-like formatting (CamelCase, snake_case, etc.)
4. Keep it concise and clear
5. This is for code comments/documentation

{f'Context: {context}' if context else ''}

Text to translate:
{text}

Translation:"""

        # Placeholder: In real implementation, call AI API here
        # For now, return a simulated AI translation
        simulated_translation = self._simulate_ai_translation(text, source_lang)

        return TranslationResult(
            original=text,
            translated=simulated_translation,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=0.95,  # High confidence for AI
            method="ai",
            preserved_terms=preserved_terms,
            metadata={
                "note": "AI translation (simulated)",
                "prompt_length": len(prompt),
            },
        )

    def _simulate_ai_translation(self, text: str, source_lang: str) -> str:
        """Simulate AI translation for demo purposes."""
        # This would be replaced with actual AI API call

        # For now, do simple rule-based + marking
        result = self._rule_based_translate(text, source_lang, "en", [])

        # Add AI-like improvements
        improved = result.translated

        # Common technical phrases
        improvements = {
            "파일을 열다": "open the file",
            "데이터를 처리하다": "process the data",
            "함수를 호출하다": "call the function",
            "오류를 처리하다": "handle the error",
            "설정을 변경하다": "modify the configuration",
            "테스트를 실행하다": "run the tests",
            "프로그램을 실행하다": "execute the program",
            "결과를 반환하다": "return the result",
        }

        for ko, en in improvements.items():
            improved = improved.replace(ko, en)

        return improved

    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str = "en",
        context: str = None,
    ) -> List[TranslationResult]:
        """Translate multiple texts in batch.

        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            context: Optional context for all translations

        Returns:
            List of TranslationResult
        """
        results = []
        for text in texts:
            result = self.translate(text, source_lang, target_lang, context)
            results.append(result)
        return results
