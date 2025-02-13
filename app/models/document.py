"""
SQLAlchemy models for the RAG Document Analyzer system.
"""
from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Index, Enum, Float, Table, Text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import enum

Base = declarative_base()

class ProcessingStatus(enum.Enum):
    """Enumeration of possible document processing statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_UPDATE = "needs_update"

class Document(Base):
    """Model for storing document information and metadata."""
    __tablename__ = "documents"
    
    # Primary key and identification
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Basic information
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_format: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # File paths
    original_path: Mapped[str] = mapped_column(String(512), nullable=False)
    processed_path: Mapped[Optional[str]] = mapped_column(String(512))
    
    # Metadata
    author: Mapped[Optional[str]] = mapped_column(String(255))
    creation_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    metadata: Mapped[Dict] = mapped_column(JSONB, default=dict)
    
    # Processing status
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus),
        nullable=False,
        default=ProcessingStatus.PENDING
    )
    status_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Document metrics
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    character_count: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    analysis_results: Mapped[List["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="document",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('ix_documents_status', 'status'),
        Index('ix_documents_created_at', 'created_at'),
        Index('ix_documents_title_trgm', 'title', postgresql_using='gin'),
        {'postgresql_partition_by': 'RANGE (created_at)'}
    )

class DocumentChunk(Base):
    """Model for storing document chunks with vector embeddings."""
    __tablename__ = "document_chunks"
    
    # Primary key and identification
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Chunk content and position
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_position: Mapped[int] = mapped_column(Integer, nullable=False)
    end_position: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Vector embedding
    embedding: Mapped[List[float]] = mapped_column(
        Vector(384),  # Dimension depends on the model
        nullable=True
    )
    
    # Chunk metadata
    metadata: Mapped[Dict] = mapped_column(JSONB, default=dict)
    section_title: Mapped[Optional[str]] = mapped_column(String(255))
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Quality metrics
    chunk_quality: Mapped[Optional[float]] = mapped_column(Float)
    relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks"
    )
    
    # Indexes
    __table_args__ = (
        Index('ix_chunks_document_id', 'document_id'),
        Index('ix_chunks_embedding', 'embedding', postgresql_using='ivfflat'),
        Index('ix_chunks_content_trgm', 'content', postgresql_using='gin'),
        {'postgresql_partition_by': 'RANGE (created_at)'}
    )

class AnalysisResult(Base):
    """Model for storing document analysis results."""
    __tablename__ = "analysis_results"
    
    # Primary key and identification
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('documents.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Analysis scores
    quality_score: Mapped[Optional[float]] = mapped_column(Float)
    coherence_score: Mapped[Optional[float]] = mapped_column(Float)
    readability_score: Mapped[Optional[float]] = mapped_column(Float)
    information_density: Mapped[Optional[float]] = mapped_column(Float)
    
    # Analysis details
    detected_anomalies: Mapped[List[Dict]] = mapped_column(ARRAY(JSONB), default=list)
    analysis_metadata: Mapped[Dict] = mapped_column(
        JSONB,
        comment='Analysis parameters, model versions, etc.',
        default=dict
    )
    
    # Analysis summary
    summary: Mapped[Optional[str]] = mapped_column(Text)
    key_findings: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Processing information
    processing_time: Mapped[float] = mapped_column(
        Float,
        comment='Processing time in seconds'
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        comment='Version of the analysis model used'
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="analysis_results"
    )
    
    # Indexes
    __table_args__ = (
        Index('ix_analysis_document_id', 'document_id'),
        Index('ix_analysis_created_at', 'created_at'),
        {'postgresql_partition_by': 'RANGE (created_at)'}
    )

# Helper function to create database tables
def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(engine)
