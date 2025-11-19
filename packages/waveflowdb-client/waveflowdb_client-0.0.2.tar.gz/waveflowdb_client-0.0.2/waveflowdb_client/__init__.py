__version__ = "1.0.0"

from .client import VectorLakeClient
from .config import Config
from .exceptions import APIError, FileProcessingError
from .models import DocumentInfo, ChatResponse, MatchingDocsResponse, HealthResponse, BatchResult

__all__ = [
    "VectorLakeClient",
    "Config",
    "APIError",
    "FileProcessingError",
    "DocumentInfo",
    "ChatResponse",
    "MatchingDocsResponse",
    "HealthResponse",
    "BatchResult",
]
