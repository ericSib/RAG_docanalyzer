from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON)  # Pour stocker le vecteur du document
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec les chunks
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    
    def set_embedding(self, embedding_array):
        """Stocke l'embedding comme JSON."""
        self.embedding = embedding_array.tolist()
    
    def get_embedding(self):
        """Récupère l'embedding."""
        return self.embedding

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON)  # Pour stocker le vecteur du chunk
    
    # Relation avec le document parent
    document = relationship("Document", back_populates="chunks")
    
    def set_embedding(self, embedding_array):
        """Stocke l'embedding comme JSON."""
        self.embedding = embedding_array.tolist()
    
    def get_embedding(self):
        """Récupère l'embedding."""
        return self.embedding
