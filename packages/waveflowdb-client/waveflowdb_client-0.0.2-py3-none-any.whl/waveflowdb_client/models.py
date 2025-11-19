from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class DocumentInfo:
    filename: str
    content: str
    size: int
    modified_time: Optional[datetime] = None

@dataclass
class ChatResponse:
    response: str
    query: str
    session_id: str
    user_id: str
    timestamp: datetime

@dataclass
class MatchingDocsResponse:
    status: str
    query: str
    response: str
    with_data: bool
    session_id: str
    user_id: str
    timestamp: datetime

@dataclass
class HealthResponse:
    status: str
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

@dataclass
class BatchResult:
    batch_number: int
    response: Any
    files_processed: List[str]
    success: bool
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
