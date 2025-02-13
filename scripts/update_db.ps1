Write-Host "Mise à jour du schéma de la base de données..." -ForegroundColor Yellow

# Variables de connexion
$POSTGRES_USER = "postgres"  # Superutilisateur PostgreSQL
$DB_USER = "rag_app_user"
$DB_NAME = "rag_doc_analyzer"
$PSQL_PATH = "C:\Program Files\PostgreSQL\16\bin\psql.exe"

# Vérification de psql
if (-not (Test-Path $PSQL_PATH)) {
    Write-Host "Erreur : psql n'a pas été trouvé à l'emplacement : $PSQL_PATH" -ForegroundColor Red
    Write-Host "Veuillez installer PostgreSQL ou mettre à jour le chemin dans ce script." -ForegroundColor Red
    exit 1
}

# Exécution du script SQL en tant que superutilisateur
Write-Host "`n1. Application des modifications..." -ForegroundColor Yellow
& $PSQL_PATH -U $POSTGRES_USER -d $DB_NAME -f .\scripts\update_db_schema.sql

# Attribution des droits à l'utilisateur de l'application
Write-Host "`n2. Attribution des droits..." -ForegroundColor Yellow
$GRANT_SCRIPT = @"
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
"@
$GRANT_SCRIPT | & $PSQL_PATH -U $POSTGRES_USER -d $DB_NAME

Write-Host "`nAppuyez sur une touche pour continuer..."
pause
