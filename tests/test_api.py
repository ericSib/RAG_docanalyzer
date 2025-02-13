import requests
import json
from pathlib import Path
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_tests.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Classe pour stocker le résultat d'un test individuel."""
    name: str
    passed: bool
    status_code: Optional[int]
    duration: float
    response: Optional[Dict[str, Any]]
    error: Optional[str] = None
    
    def print_details(self) -> None:
        """Affiche les détails du test."""
        symbol = "+" if self.passed else "-"  # Utiliser des symboles ASCII au lieu des caractères Unicode
        logger.info(f"\n{symbol} {self.name}")
        logger.info(f"  Status: {self.status_code}")
        logger.info(f"  Durée: {self.duration:.2f}s")
        
        if not self.passed and self.error:
            logger.error(f"  Erreur: {self.error}")
        
        if self.response:
            logger.info("  Réponse:")
            logger.info(json.dumps(self.response, indent=2, ensure_ascii=False))

@dataclass
class TestSuite:
    """Classe pour gérer une suite de tests."""
    results: list[TestResult] = field(default_factory=list)
    base_url: str = "http://127.0.0.1:8000"
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return self.total - self.passed
    
    def add_result(self, result: TestResult) -> None:
        """Ajoute un résultat de test."""
        self.results.append(result)
        
    def print_summary(self) -> None:
        """Affiche le résumé des tests."""
        logger.info("\n=== Résumé des tests ===")
        logger.info(f"Tests effectués: {self.total}")
        logger.info(f"Tests réussis: {self.passed}")
        logger.info(f"Tests échoués: {self.failed}")
        
        if self.results:
            logger.info("\nDétails des tests:")
            for result in self.results:
                result.print_details()
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        test_name: str,
        expected_status: int = 200,
        **kwargs
    ) -> TestResult:
        """Effectue une requête HTTP et retourne le résultat du test."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        
        try:
            response = requests.request(method, url, **kwargs)
            duration = time.time() - start_time
            
            try:
                response_json = response.json() if response.content else None
            except json.JSONDecodeError:
                return TestResult(
                    name=test_name,
                    passed=False,
                    status_code=response.status_code,
                    duration=duration,
                    response=None,
                    error="Réponse JSON invalide"
                )
            
            # Vérification du statut de la réponse
            passed = response.status_code == expected_status
            if passed and response_json:
                # Pour le health check
                if "health" in response_json:
                    passed = response_json["health"] == "healthy"
                # Pour les autres endpoints
                elif "status" in response_json:
                    passed = response_json["status"] == "success"
            
            return TestResult(
                name=test_name,
                passed=passed,
                status_code=response.status_code,
                duration=duration,
                response=response_json
            )
            
        except requests.RequestException as e:
            return TestResult(
                name=test_name,
                passed=False,
                status_code=None,
                duration=time.time() - start_time,
                response=None,
                error=str(e)
            )
    
    def test_health(self) -> None:
        """Test du health check."""
        logger.info("\n=== Test du health check ===")
        result = self.make_request("GET", "/health", "health")
        self.add_result(result)
    
    def test_document_analysis(self, content: str) -> None:
        """Test de l'analyse de document."""
        logger.info("\n=== Test de l'analyse de document ===")
        test_file = Path("test_document.txt")
        
        try:
            test_file.write_text(content, encoding='utf-8')
            
            with open(test_file, 'rb') as f:
                result = self.make_request(
                    "POST",
                    "/documents/analyze",
                    "document_analysis",
                    files={'file': ('test_document.txt', f, 'text/plain')}
                )
            
            self.add_result(result)
            
        except Exception as e:
            self.add_result(TestResult(
                name="document_analysis",
                passed=False,
                status_code=None,
                duration=0,
                response=None,
                error=str(e)
            ))
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_semantic_search(self) -> None:
        """Test de la recherche sémantique."""
        logger.info("\n=== Test de la recherche sémantique ===")
        
        payload = {
            "query": "fonctionnement système",
            "limit": 5
        }
        
        try:
            logger.info(f"Envoi requête: {json.dumps(payload, ensure_ascii=False)}")
            
            result = self.make_request(
                method="POST",
                endpoint="/search",
                test_name="semantic_search",
                expected_status=200,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                json=payload
            )
            
            # Validation spécifique de la réponse de recherche
            if result.response:
                result.passed = (
                    result.status_code == 200 and
                    isinstance(result.response, dict) and
                    result.response.get("status") == "success" and
                    isinstance(result.response.get("results"), list) and
                    isinstance(result.response.get("count"), int)
                )
                
                if not result.passed:
                    result.error = "Format de réponse invalide"
                    logger.error(f"Réponse reçue: {json.dumps(result.response, indent=2)}")
            
            self.add_result(result)
            
        except Exception as e:
            logger.error(f"Erreur test recherche: {str(e)}")
            self.add_result(TestResult(
                name="semantic_search",
                passed=False,
                status_code=None,
                duration=0.0,
                response=None,
                error=str(e)
            ))

def main():
    """Fonction principale d'exécution des tests."""
    logger.info("Démarrage des tests de l'API...")
    
    # Création de la suite de tests
    suite = TestSuite()
    
    # Test 1: Health Check
    suite.test_health()
    
    # Test 2: Document Analysis
    test_doc = """
    Ceci est un document de test pour l'analyseur RAG.
    Il contient plusieurs phrases pour tester le chunking.
    Nous voulons voir comment le système gère le texte.
    L'objectif est de vérifier le bon fonctionnement de l'API.
    Le document contient suffisamment de texte pour créer plusieurs chunks.
    Chaque chunk sera analysé et indexé séparément.
    Les embeddings seront générés pour permettre la recherche sémantique.
    """
    suite.test_document_analysis(test_doc)
    
    # Test 3: Semantic Search
    suite.test_semantic_search()
    
    # Affichage du résumé
    suite.print_summary()
    
    # Sortir avec un code d'erreur si des tests ont échoué
    if suite.failed > 0:
        logger.error(f"\n{suite.failed} test(s) ont échoué!")
        exit(1)
    else:
        logger.info("\nTous les tests ont réussi!")
        exit(0)

if __name__ == "__main__":
    main()
