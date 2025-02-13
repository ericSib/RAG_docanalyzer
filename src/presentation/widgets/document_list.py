"""Widget de liste des documents."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal

from ...core.domain import Document

class DocumentListWidget(QWidget):
    """Widget affichant la liste des documents."""
    
    document_selected = pyqtSignal(Document)
    
    def __init__(self, parent=None):
        """Initialise le widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)
        
        # Liste des documents
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        self.setLayout(layout)
    
    def add_document(self, document: Document):
        """Ajoute un document à la liste."""
        item = QListWidgetItem(document.name)
        item.setData(1, document)
        self.list_widget.addItem(item)
    
    def clear(self):
        """Vide la liste."""
        self.list_widget.clear()
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Gère le clic sur un document."""
        document = item.data(1)
        self.document_selected.emit(document)
