from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QFileDialog, QProgressBar, QLabel, 
                            QTableWidget, QTableWidgetItem, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
from pathlib import Path
import json
from datetime import datetime
from .analyzer import analyzer
from .storage import storage
from .config import config

class AnalyzerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            # Vérification de la taille du fichier
            file_size = Path(self.file_path).stat().st_size
            if file_size > config.max_file_size:
                raise ValueError(f"Le fichier est trop volumineux (max: {config.max_file_size/1024/1024:.1f}MB)")
            
            self.progress.emit(10)
            
            # Analyse du document
            result = analyzer.analyze_document(self.file_path)
            
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAG Document Analyzer")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Onglets
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Onglet Analyse
        analyze_tab = QWidget()
        analyze_layout = QVBoxLayout(analyze_tab)
        
        self.analyze_btn = QPushButton("Analyser un document")
        self.analyze_btn.clicked.connect(self.start_analysis)
        analyze_layout.addWidget(self.analyze_btn)

        self.progress = QProgressBar()
        analyze_layout.addWidget(self.progress)

        self.results_label = QLabel()
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        analyze_layout.addWidget(self.results_label)

        tabs.addTab(analyze_tab, "Analyse")

        # Onglet Documents Récents
        recent_tab = QWidget()
        recent_layout = QVBoxLayout(recent_tab)
        
        self.documents_table = QTableWidget()
        self.documents_table.setColumnCount(3)
        self.documents_table.setHorizontalHeaderLabels(["Nom", "Date", "Résumé"])
        self.documents_table.horizontalHeader().setStretchLastSection(True)
        recent_layout.addWidget(self.documents_table)
        
        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.load_recent_documents)
        recent_layout.addWidget(refresh_btn)

        tabs.addTab(recent_tab, "Documents Récents")

        # Chargement initial des documents récents
        self.load_recent_documents()

    def load_recent_documents(self):
        """Charge les documents récents dans le tableau."""
        documents = storage.get_recent_documents()
        self.documents_table.setRowCount(len(documents))
        
        for i, doc in enumerate(documents):
            self.documents_table.setItem(i, 0, QTableWidgetItem(doc['filename']))
            date = datetime.fromisoformat(doc['created_at'])
            self.documents_table.setItem(i, 1, QTableWidgetItem(date.strftime('%Y-%m-%d %H:%M')))
            
            # Récupération du résumé de la dernière analyse
            with storage.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT summary FROM analyses WHERE document_id = ? ORDER BY created_at DESC LIMIT 1',
                    (doc['id'],)
                )
                result = cursor.fetchone()
                summary = result[0] if result else "Pas d'analyse"
            
            self.documents_table.setItem(i, 2, QTableWidgetItem(summary))

    def start_analysis(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un document",
            str(config.data_dir),
            "Documents (*.txt *.md *.pdf)"
        )
        
        if file_path:
            self.analyze_btn.setEnabled(False)
            self.analyzer_thread = AnalyzerThread(file_path)
            self.analyzer_thread.progress.connect(self.update_progress)
            self.analyzer_thread.finished.connect(self.analysis_complete)
            self.analyzer_thread.error.connect(self.analysis_error)
            self.analyzer_thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def analysis_complete(self, results):
        self.analyze_btn.setEnabled(True)
        self.results_label.setText(
            f"Analyse terminée !\n"
            f"Document ID: {results['document_id']}\n"
            f"Analyse ID: {results['analysis_id']}\n"
            f"Nombre de chunks: {results['num_chunks']}\n"
            f"Résumé: {results['summary']}"
        )
        self.load_recent_documents()

    def analysis_error(self, error_msg):
        self.analyze_btn.setEnabled(True)
        self.results_label.setText(f"Erreur: {error_msg}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
