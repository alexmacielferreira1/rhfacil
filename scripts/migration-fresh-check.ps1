$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$backendRoot = Join-Path $projectRoot 'backend'
$databaseName = "gestao_de_funcionarios_migration_check_$PID"
if ($databaseName -notmatch '^gestao_de_funcionarios_migration_check_[0-9]+$') {
    throw 'Nome do banco descartável não passou na validação de segurança.'
}

$databaseCreated = $false
Push-Location $projectRoot
try {
    docker compose exec -T postgres createdb -U gestao_de_funcionarios $databaseName
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o banco descartável.' }
    $databaseCreated = $true

    $migrationUrl = "postgresql+asyncpg://gestao_de_funcionarios:local_only_change_me@localhost:12547/$databaseName"
    $env:APP_ENV = 'test'
    $env:DATABASE_URL = $migrationUrl
    $env:MIGRATION_DATABASE_URL = $migrationUrl
    $env:REDIS_URL = 'redis://localhost:13547/0'

    Push-Location $backendRoot
    try {
        & .\.venv\Scripts\alembic.exe upgrade head
        if ($LASTEXITCODE -ne 0) { throw 'Alembic não chegou ao head no banco vazio.' }
    }
    finally { Pop-Location }

    $revision = docker compose exec -T postgres psql -U gestao_de_funcionarios -d $databaseName -Atc 'select version_num from alembic_version'
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível ler a revisão aplicada.' }
    if ($revision.Trim() -ne '20260828_0010') {
        throw "Revisão inesperada no banco vazio: $revision"
    }

    $tableCount = docker compose exec -T postgres psql -U gestao_de_funcionarios -d $databaseName -Atc "select count(*) from information_schema.tables where table_schema = 'public'"
    if ($LASTEXITCODE -ne 0 -or [int]$tableCount -lt 16) {
        throw 'O esquema criado no banco vazio está incompleto.'
    }

    Write-Output 'Migrations aprovadas em banco vazio descartável.'
}
finally {
    if ($databaseCreated) {
        docker compose exec -T postgres dropdb -U gestao_de_funcionarios --if-exists $databaseName | Out-Null
    }
    Pop-Location
}
