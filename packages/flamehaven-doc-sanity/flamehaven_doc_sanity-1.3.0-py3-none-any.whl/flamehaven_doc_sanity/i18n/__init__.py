"""I18n (Internationalization) module for Flamehaven-Doc-Sanity.

This module provides AI-powered translation with meta-cognitive validation
for non-English developers to seamlessly publish on GitHub.

Features:
- Automatic language detection
- Code comment translation (# comments, docstrings)
- README/documentation translation
- Meta-cognitive quality validation
- Terminology consistency enforcement
- Self-learning translation improvement

Inspired by DFI-META's meta-cognitive evolution system.
"""

from flamehaven_doc_sanity.i18n.code_comment_parser import CodeCommentParser
from flamehaven_doc_sanity.i18n.language_detector import LanguageDetector
from flamehaven_doc_sanity.i18n.metacognition import (
    ConsistencyChecker,
    ContextAnalyzer,
    TranslationQualityOracle,
)
from flamehaven_doc_sanity.i18n.translator import TranslationEngine

__all__ = [
    "LanguageDetector",
    "CodeCommentParser",
    "TranslationEngine",
    "TranslationQualityOracle",
    "ConsistencyChecker",
    "ContextAnalyzer",
]
