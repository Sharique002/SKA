"""
Data models and schemas for the SKA system
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Schema for document metadata"""
    id: Optional[int] = None
    filename: str
    file_type: str
    upload_date: datetime
    file_size: int
    num_chunks: int
    status: str = "processed"


class ChunkData(BaseModel):
    """Schema for text chunks"""
    chunk_id: str
    document_id: int
    content: str
    chunk_index: int
    metadata: dict


class QueryRequest(BaseModel):
    """Schema for query requests"""
    query: str
    top_k: Optional[int] = 5
    filter_docs: Optional[List[int]] = None


class QueryResponse(BaseModel):
    """Schema for query responses"""
    answer: str
    sources: List[dict]
    confidence: float
    processing_time: float


class UploadResponse(BaseModel):
    """Schema for upload responses"""
    success: bool
    message: str
    document_id: Optional[int] = None
    filename: str
    num_chunks: int
