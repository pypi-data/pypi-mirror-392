"""Response models and metadata for PromptGuard."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Any, Union, Dict, List
from enum import Enum
import json
from pydantic import BaseModel


class LogLevel(str, Enum):
    """Log level enum."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ExecutionMetadata:
    """Metadata about prompt execution."""
    model_used: str
    provider: str
    attempts: int
    execution_time_ms: float
    tokens_used: Dict[str, int]  # {input: X, output: Y, total: Z}
    estimated_cost: float
    cached: bool
    cache_key: Optional[str] = None
    retry_history: List[dict] = field(default_factory=list)  # [{attempt: 1, error: "...", delay: 2.0}]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class PromptResult:
    """Result of prompt execution."""
    
    def __init__(
        self,
        success: bool,
        response: Optional[Union[str, BaseModel]] = None,
        raw_response: Any = None,
        metadata: Optional[ExecutionMetadata] = None,
        error: Optional[Exception] = None,
        validation_results: Optional[dict] = None,
    ):
        self.success = success
        self.response = response
        self.raw_response = raw_response
        self.metadata = metadata
        self.error = error
        self.validation_results = validation_results or {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        response_data = None
        if self.response is not None:
            if isinstance(self.response, BaseModel):
                response_data = self.response.model_dump()
            else:
                response_data = self.response
        
        return {
            'success': self.success,
            'response': response_data,
            'error': str(self.error) if self.error else None,
            'metadata': self.metadata.to_dict() if self.metadata else None,
            'validation_results': self.validation_results,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class StreamChunk:
    """Single chunk from streaming response."""
    delta: str
    accumulated_text: str
    metadata: Optional[dict] = None
    finished: bool = False


@dataclass
class ValidationResult:
    """Result from a single validator."""
    passed: bool
    confidence: float  # 0.0 to 1.0
    message: str
    details: Optional[dict] = None
