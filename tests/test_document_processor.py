import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from rag_doc_analyzer.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        """Configuration initiale pour chaque test."""
        self.db_session = MagicMock()
        with patch('sentence_transformers.SentenceTransformer'), \
             patch('spacy.load'):
            self.processor = DocumentProcessor(self.db_session)
        
        # Mock des dépendances communes
        self.processor.model = MagicMock()
        self.processor.nlp = MagicMock()

    def test_process_document(self):
        """Test du traitement complet d'un document."""
        # Configuration des mocks
        test_embedding = np.array([0.1] * 512)  # Vecteur 512D
        self.processor.model.encode.side_effect = [
            test_embedding,  # Pour l'embedding du document
            np.array([test_embedding])  # Pour l'embedding des chunks
        ]
        
        # Mock du découpage en phrases
        mock_doc = MagicMock()
        mock_doc.sents = [MagicMock(text="Ceci est un test.")]
        self.processor.nlp.return_value = mock_doc
        
        # Mock de l'insertion en base de données
        self.db_session.execute.return_value.scalar.return_value = 1  # ID du document
        
        # Test du traitement
        result = self.processor.process_document(
            content="Ceci est un test.",
            title="Test"
        )
        
        # Vérifications
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['title'], "Test")
        self.assertEqual(result['content'], "Ceci est un test.")
        self.assertIsInstance(result['chunks'], list)
        self.assertIsInstance(result['embeddings'], list)
        
        # Vérification des appels à la base de données
        self.db_session.execute.assert_called()
        self.db_session.commit.assert_called_once()

    def test_generate_chunks(self):
        """Test de la génération des chunks."""
        # Configuration du mock pour simuler un document avec plusieurs phrases
        mock_sent1 = MagicMock()
        mock_sent1.text = "Première phrase."
        mock_sent2 = MagicMock()
        mock_sent2.text = "Deuxième phrase."
        
        mock_doc = MagicMock()
        mock_doc.sents = [mock_sent1, mock_sent2]
        
        chunks = self.processor._generate_chunks(mock_doc)
        
        # Vérifications
        self.assertIsInstance(chunks, list)
        self.assertTrue(all(isinstance(chunk, str) for chunk in chunks))
        self.assertEqual(len(chunks), 1)  # Les deux phrases devraient être dans un seul chunk
        self.assertIn("Première phrase. Deuxième phrase.", chunks)

    def test_semantic_search(self):
        """Test de la recherche sémantique."""
        # Configuration des mocks
        test_embedding = np.array([0.1] * 512)  # Vecteur 512D
        self.processor.model.encode.return_value = test_embedding
        
        # Mock des résultats de recherche
        mock_result = MagicMock()
        mock_result.id = 1
        mock_result.title = "Test Document"
        mock_result.content = "Contenu de test" * 20  # Pour tester la prévisualisation
        mock_result.distance = 0.1
        
        self.db_session.execute.return_value.fetchall.return_value = [mock_result]
        
        # Test de la recherche
        results = self.processor.semantic_search("requête test", limit=1)
        
        # Vérifications
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 1)
        self.assertEqual(results[0]['title'], "Test Document")
        self.assertTrue(results[0]['preview'].endswith('...'))
        self.assertAlmostEqual(results[0]['similarity'], 0.9)  # 1.0 - 0.1
        
        # Vérification des appels
        self.processor.model.encode.assert_called_once_with("requête test")
        self.db_session.execute.assert_called()

    def test_error_handling(self):
        """Test de la gestion des erreurs."""
        # Test d'erreur lors du traitement d'un document
        self.db_session.execute.side_effect = Exception("Erreur de base de données")
        
        with self.assertRaises(Exception):
            self.processor.process_document("Test", "Test")
        
        # Vérification que le rollback a été appelé
        self.db_session.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()
