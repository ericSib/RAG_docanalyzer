"""Tests end-to-end pour l'interface graphique."""
import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from src.presentation.main_window import MainWindow

@pytest.fixture(scope="module")
def app():
    """Crée l'application Qt pour les tests."""
    return QApplication(sys.argv)

@pytest.fixture
def main_window(app, test_config):
    """Crée la fenêtre principale pour les tests."""
    window = MainWindow(config=test_config)
    window.show()
    return window

def test_document_upload(main_window, test_documents_dir, qtbot):
    """Test le téléchargement et l'analyse d'un document via l'interface."""
    # Créer un document test
    test_file = test_documents_dir / "test.txt"
    test_file.write_text("Ceci est un document de test pour l'interface graphique.")
    
    # Simuler le drag & drop du fichier
    main_window.handle_file_drop([str(test_file)])
    
    # Attendre que l'analyse soit terminée
    qtbot.wait_until(lambda: main_window.document_list.count() > 0)
    
    # Vérifier que le document apparaît dans la liste
    assert main_window.document_list.count() == 1
    
    # Vérifier que l'analyse est complète
    item = main_window.document_list.item(0)
    assert "Completed" in item.text()

def test_search_functionality(main_window, qtbot):
    """Test la fonctionnalité de recherche dans l'interface."""
    # Entrer une requête de recherche
    search_input = main_window.search_input
    QTest.keyClicks(search_input, "test query")
    
    # Simuler l'appui sur Entrée
    QTest.keyClick(search_input, Qt.Key.Key_Return)
    
    # Attendre les résultats
    qtbot.wait_until(lambda: main_window.results_list.count() > 0)
    
    # Vérifier qu'il y a des résultats
    assert main_window.results_list.count() > 0
