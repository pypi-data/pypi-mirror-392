"""Validation system for PromptGuard."""
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import re


@dataclass
class ValidationResult:
    """Result from a single validator."""
    passed: bool
    confidence: float  # 0.0 to 1.0
    message: str
    details: Optional[dict] = None


class Validator(ABC):
    """Base class for response validators."""
    
    @abstractmethod
    async def validate(
        self,
        response: str,
        context: Optional[dict] = None
    ) -> ValidationResult:
        """Validate response and return result.
        
        Args:
            response: Response text to validate
            context: Additional context for validation
            
        Returns:
            ValidationResult
        """
        pass


class LengthValidator(Validator):
    """Validate response length."""
    
    def __init__(self, min_chars: int = 0, max_chars: Optional[int] = None):
        self.min_chars = min_chars
        self.max_chars = max_chars
    
    async def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
        """Validate response length."""
        length = len(response)
        
        if self.min_chars and length < self.min_chars:
            return ValidationResult(
                passed=False,
                confidence=0.0,
                message=f"Response too short: {length} < {self.min_chars}",
                details={"length": length}
            )
        
        if self.max_chars and length > self.max_chars:
            return ValidationResult(
                passed=False,
                confidence=0.0,
                message=f"Response too long: {length} > {self.max_chars}",
                details={"length": length}
            )
        
        return ValidationResult(
            passed=True,
            confidence=1.0,
            message=f"Length validation passed: {length} chars",
            details={"length": length}
        )


class KeywordValidator(Validator):
    """Ensure response contains required keywords."""
    
    def __init__(self, keywords: List[str], require_all: bool = False):
        self.keywords = [k.lower() for k in keywords]
        self.require_all = require_all
    
    async def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
        """Validate required keywords."""
        response_lower = response.lower()
        found_keywords = [k for k in self.keywords if k in response_lower]
        
        if self.require_all:
            if len(found_keywords) < len(self.keywords):
                missing = set(self.keywords) - set(found_keywords)
                return ValidationResult(
                    passed=False,
                    confidence=0.0,
                    message=f"Missing required keywords: {missing}",
                    details={"found": found_keywords, "missing": list(missing)}
                )
        else:
            if not found_keywords:
                return ValidationResult(
                    passed=False,
                    confidence=0.0,
                    message=f"No keywords found from: {self.keywords}",
                    details={"found": found_keywords}
                )
        
        return ValidationResult(
            passed=True,
            confidence=len(found_keywords) / len(self.keywords),
            message=f"Keyword validation passed: {len(found_keywords)} found",
            details={"found": found_keywords}
        )


class CitationValidator(Validator):
    """Ensure response has proper citations."""
    
    def __init__(self, required: bool = True):
        self.required = required
    
    async def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
        """Validate citations."""
        # Look for common citation patterns
        patterns = [
            r'\[\d+\]',  # [1] style
            r'\(.*?\d{4}.*?\)',  # (Author 2024) style
            r'According to',
            r'According to.*?:',
            r'As stated in',
        ]
        
        has_citation = any(re.search(pattern, response, re.IGNORECASE) for pattern in patterns)
        
        if self.required and not has_citation:
            return ValidationResult(
                passed=False,
                confidence=0.0,
                message="Response lacks citations",
                details={"has_citation": False}
            )
        
        return ValidationResult(
            passed=True,
            confidence=1.0 if has_citation else 0.5,
            message="Citation validation passed",
            details={"has_citation": has_citation}
        )


class NoHallucinationValidator(Validator):
    """Detect hallucinations by checking against source documents."""
    
    def __init__(self, source_docs: List[str], threshold: float = 0.8):
        self.source_docs = source_docs
        self.threshold = threshold
    
    async def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
        """Validate against hallucinations."""
        # Simple check: see if key entities appear in source docs
        # In production, use embedding similarity or NLI models
        
        # For now, use simple word overlap
        response_words = set(response.lower().split())
        doc_words = set(" ".join(self.source_docs).lower().split())
        
        overlap = len(response_words & doc_words) / len(response_words) if response_words else 0
        
        if overlap < self.threshold:
            return ValidationResult(
                passed=False,
                confidence=1 - overlap,
                message=f"Potential hallucination detected (overlap: {overlap:.2%})",
                details={"overlap_ratio": overlap}
            )
        
        return ValidationResult(
            passed=True,
            confidence=overlap,
            message=f"No hallucination detected (overlap: {overlap:.2%})",
            details={"overlap_ratio": overlap}
        )


class SentimentValidator(Validator):
    """Check response sentiment."""
    
    def __init__(self, allowed: Optional[List[str]] = None):
        self.allowed = allowed or ["neutral", "positive", "negative"]
    
    async def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
        """Validate sentiment."""
        # Simple sentiment detection based on keywords
        positive_words = {"good", "great", "excellent", "love", "amazing", "wonderful"}
        negative_words = {"bad", "terrible", "hate", "awful", "horrible", "worst"}
        
        pos_count = sum(1 for word in positive_words if word in response.lower())
        neg_count = sum(1 for word in negative_words if word in response.lower())
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        if sentiment not in self.allowed:
            return ValidationResult(
                passed=False,
                confidence=0.0,
                message=f"Sentiment '{sentiment}' not allowed",
                details={"sentiment": sentiment, "allowed": self.allowed}
            )
        
        return ValidationResult(
            passed=True,
            confidence=1.0,
            message=f"Sentiment validation passed: {sentiment}",
            details={"sentiment": sentiment}
        )


# Convenience functions
def length_range(min_chars: int = 0, max_chars: Optional[int] = None) -> LengthValidator:
    """Create length validator."""
    return LengthValidator(min_chars, max_chars)


def contains_keywords(keywords: List[str], require_all: bool = False) -> KeywordValidator:
    """Create keyword validator."""
    return KeywordValidator(keywords, require_all)


def has_citations(required: bool = True) -> CitationValidator:
    """Create citation validator."""
    return CitationValidator(required)


def no_hallucination(source_docs: List[str], threshold: float = 0.8) -> NoHallucinationValidator:
    """Create no-hallucination validator."""
    return NoHallucinationValidator(source_docs, threshold)


def sentiment_check(allowed: Optional[List[str]] = None) -> SentimentValidator:
    """Create sentiment validator."""
    return SentimentValidator(allowed)
