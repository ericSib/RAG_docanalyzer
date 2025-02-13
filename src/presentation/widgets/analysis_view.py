"""Widget d'affichage des résultats d'analyse."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import pyqtSignal

from ...core.domain import AnalysisResult

class AnalysisViewWidget(QWidget):
    """Widget affichant les résultats d'analyse."""
    
    def __init__(self, parent=None):
        """Initialise le widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)
        
        # Zone de texte pour les résultats
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
    
    def display_analysis(self, analysis: AnalysisResult):
        """Affiche les résultats d'une analyse."""
        self.text_edit.clear()
        
        # Affiche chaque chunk
        for chunk in analysis.chunks:
            self.text_edit.append(f"Chunk {chunk.id}:")
            self.text_edit.append(chunk.content)
            self.text_edit.append("\n")
    
    def clear(self):
        """Efface les résultats."""
        self.text_edit.clear()
