from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# RAG Query Schemas
class RAGQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's query message")
    selected_text: Optional[str] = Field(None, max_length=5000, description="Selected text for contextual queries")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to return")

class SourceInfo(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    content: str = Field(..., max_length=5000, description="Content snippet")
    source_file: str = Field(..., max_length=500, description="Source document")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class RAGQueryResponse(BaseModel):
    query: str = Field(..., description="The original query")
    response: str = Field(..., max_length=10000, description="The AI-generated response")
    sources: List[SourceInfo] = Field(default_factory=list, description="Sources used in the response")
    selected_text_used: Optional[str] = Field(None, description="Text that was used as context")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

# Search Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to return")

class SearchResult(BaseModel):
    id: int = Field(..., ge=0, description="Result identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    content: str = Field(..., max_length=5000, description="Content snippet")
    source_file: str = Field(..., max_length=500, description="Source document")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    query: str = Field(..., description="The original query")
    total_results: int = Field(..., ge=0, description="Total number of results found")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

# Session Schemas
class ChatSessionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="User identifier")
    session_name: Optional[str] = Field(None, max_length=200, description="Session name")

class ChatSessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    client_secret: str = Field(..., description="Client secret for secure communication")
    expires_at: int = Field(..., ge=0, description="Expiration timestamp")
    user_id: str = Field(..., description="User identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")