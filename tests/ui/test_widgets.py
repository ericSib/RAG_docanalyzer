"""Tests pour les widgets Qt."""
import pytest
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QApplication
import sys

from src.core.domain import Document, AnalysisResult, DocumentChunk
from src.ui.widgets.document_list import DocumentListWidget
from src.ui.widgets.analysis_view import AnalysisViewWidget

# Fixture pour l'application Qt
@pytest.fixture
def app():
    """Crée une instance de QApplication."""
    app = QApplication(sys.argv)
    yield app
    app.quit()

def test_document_list_widget(app):
    """Test le widget de liste des documents."""
    # Arrange
    widget = DocumentListWidget()
    doc = Document(
        id="doc123",
        path=Path("/test/doc.txt"),
        name="doc.txt",
        content="Test content",
        created_at=datetime.now()
    )
    
    # Act
    widget.add_document(doc)
    
    # Assert
    assert widget.list_widget.count() == 1
    item = widget.list_widget.item(0)
    assert item.text() == doc.name
    assert item.data(1) == doc

def test_analysis_view_widget(app):
    """Test le widget d'affichage des analyses."""
    # Arrange
    widget = AnalysisViewWidget()
    analysis = AnalysisResult(
        id="analysis123",
        document_id="doc123",
        chunks=[
            DocumentChunk(
                id="chunk1",
                content="Test chunk 1",
                start_index=0,
                end_index=10
            ),
            DocumentChunk(
                id="chunk2",
                content="Test chunk 2",
                start_index=11,
                end_index=20
            )
        ],
        created_at=datetime.now()
    )
    
    # Act
    widget.display_analysis(analysis)
    
    # Assert
    text = widget.text_edit.toPlainText()
    assert "Test chunk 1" in text
    assert "Test chunk 2" in text
