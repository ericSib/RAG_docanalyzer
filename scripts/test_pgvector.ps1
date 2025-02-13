# Importer la configuration
. "$PSScriptRoot\setup_config.ps1"

function Test-PgVector {
    param (
        [Parameter(Mandatory=$false)]
        [hashtable]$UserConfig = @{}
    )

    $config = Initialize-Configuration $UserConfig
    $env:PGPASSWORD = $config.PG_PASSWORD

    Write-Host "Testing pgvector installation..." -ForegroundColor Cyan

    # Test 1: Vérifier les fichiers
    Write-Host "`nTest 1: Checking installed files..." -ForegroundColor Yellow
    $files = @(
        @{Path = Join-Path $config.PG_LIB "vector.dll"; Name = "Vector DLL"},
        @{Path = Join-Path $config.PG_EXTENSION "vector.control"; Name = "Control file"},
        @{Path = Join-Path $config.PG_EXTENSION "vector--$($config.PGVECTOR_VERSION).sql"; Name = "SQL file"}
    )

    $filesOk = $true
    foreach ($file in $files) {
        if (Test-Path $file.Path) {
            Write-Host "✓ $($file.Name) present" -ForegroundColor Green
        } else {
            Write-Host "✗ $($file.Name) missing" -ForegroundColor Red
            $filesOk = $false
        }
    }

    # Test 2: Vérifier l'extension dans PostgreSQL
    Write-Host "`nTest 2: Checking PostgreSQL extension..." -ForegroundColor Yellow
    $extensionQuery = "SELECT * FROM pg_extension WHERE extname = 'vector';"
    $extensionResult = & "$($config.PG_BIN)\psql.exe" -U $config.PG_USER -d postgres -t -c $extensionQuery

    if ($extensionResult) {
        Write-Host "✓ Vector extension is installed in PostgreSQL" -ForegroundColor Green
        $extensionOk = $true
    } else {
        Write-Host "✗ Vector extension is not installed in PostgreSQL" -ForegroundColor Red
        $extensionOk = $false
    }

    # Test 3: Test fonctionnel - Créer et manipuler des vecteurs
    Write-Host "`nTest 3: Testing vector functionality..." -ForegroundColor Yellow
    $testQueries = @(
        @{
            Query = "CREATE TABLE IF NOT EXISTS vector_test (id serial PRIMARY KEY, embedding vector(3));"
            Description = "Create test table"
        },
        @{
            Query = "INSERT INTO vector_test (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');"
            Description = "Insert test vectors"
        },
        @{
            Query = "SELECT * FROM vector_test WHERE embedding <-> '[3,3,3]' ORDER BY embedding <-> '[3,3,3]' LIMIT 1;"
            Description = "Test vector similarity search"
        }
    )

    $functionalOk = $true
    foreach ($test in $testQueries) {
        Write-Host "Running: $($test.Description)..." -NoNewline
        try {
            $result = & "$($config.PG_BIN)\psql.exe" -U $config.PG_USER -d postgres -c $test.Query 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host " ✓" -ForegroundColor Green
            } else {
                Write-Host " ✗" -ForegroundColor Red
                Write-Host "Error: $result" -ForegroundColor Red
                $functionalOk = $false
            }
        } catch {
            Write-Host " ✗" -ForegroundColor Red
            Write-Host "Error: $_" -ForegroundColor Red
            $functionalOk = $false
        }
    }

    # Nettoyage
    Write-Host "`nCleaning up test data..." -ForegroundColor Yellow
    & "$($config.PG_BIN)\psql.exe" -U $config.PG_USER -d postgres -c "DROP TABLE IF EXISTS vector_test;"

    # Résumé
    Write-Host "`nTest Summary:" -ForegroundColor Cyan
    Write-Host "=============" -ForegroundColor Cyan
    Write-Host "Files Test: $(if ($filesOk) {"✓ Passed"} else {"✗ Failed"})" -ForegroundColor $(if ($filesOk) {"Green"} else {"Red"})
    Write-Host "Extension Test: $(if ($extensionOk) {"✓ Passed"} else {"✗ Failed"})" -ForegroundColor $(if ($extensionOk) {"Green"} else {"Red"})
    Write-Host "Functional Test: $(if ($functionalOk) {"✓ Passed"} else {"✗ Failed"})" -ForegroundColor $(if ($functionalOk) {"Green"} else {"Red"})

    $allTestsPassed = $filesOk -and $extensionOk -and $functionalOk
    Write-Host "`nOverall Status: $(if ($allTestsPassed) {"✓ All tests passed"} else {"✗ Some tests failed"})" -ForegroundColor $(if ($allTestsPassed) {"Green"} else {"Red"})

    return $allTestsPassed
}

# Exécuter les tests
try {
    $testsPassed = Test-PgVector @{
        PG_VERSION = "16"
        PGVECTOR_VERSION = "0.6.0"
    }

    if (-not $testsPassed) {
        Write-Error "PgVector installation validation failed"
        exit 1
    }
}
catch {
    Write-Error "Test execution failed: $_"
    exit 1
}
