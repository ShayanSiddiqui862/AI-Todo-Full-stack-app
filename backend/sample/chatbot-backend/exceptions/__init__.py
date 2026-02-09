from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class APIError(BaseModel):
    """Base API error response model"""
    error: str
    detail: str
    status_code: int
    timestamp: datetime = datetime.now()
    path: Optional[str] = None

class RAGServiceError(APIError):
    """Error for RAG service failures"""
    error: str = "RAG Service Error"
    status_code: int = 500

class QdrantConnectionError(APIError):
    """Error for Qdrant connection failures"""
    error: str = "Qdrant Connection Error"
    status_code: int = 503

class DocumentProcessingError(APIError):
    """Error for document processing failures"""
    error: str = "Document Processing Error"
    status_code: int = 422

class AuthenticationError(APIError):
    """Error for authentication failures"""
    error: str = "Authentication Error"
    status_code: int = 401

class ValidationError(APIError):
    """Error for validation failures"""
    error: str = "Validation Error"
    status_code: int = 422

class NotFoundError(APIError):
    """Error for not found resources"""
    error: str = "Not Found"
    status_code: int = 404

class RateLimitError(APIError):
    """Error for rate limiting"""
    error: str = "Rate Limit Exceeded"
    status_code: int = 429

class QdrantUploadError(APIError):
    """Error for Qdrant upload failures"""
    error: str = "Qdrant Upload Error"
    status_code: int = 500