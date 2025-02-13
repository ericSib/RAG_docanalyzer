# Ajout du répertoire racine au PYTHONPATH
$env:PYTHONPATH = "C:\DEV\RAG_Doc-analyzer;$env:PYTHONPATH"

Write-Host "Test du système RAG..." -ForegroundColor Yellow

# Exécution des tests unitaires
Write-Host "`n1. Lancement des tests..." -ForegroundColor Yellow
python -m unittest tests/test_document_processor.py -v

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
