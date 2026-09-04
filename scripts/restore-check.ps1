param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$resolvedBackup = (Resolve-Path -LiteralPath $BackupFile).Path
$checksumFile = "$resolvedBackup.sha256"
$expected = (Get-Content -Raw -LiteralPath $checksumFile).Trim().ToLowerInvariant()
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedBackup).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'Checksum do backup inválido.' }

$restoreDatabase = 'gestao_de_funcionarios_restore_check'
$containerFile = '/tmp/gestao_de_funcionarios_restore_check.dump'
Push-Location $projectRoot
try {
    docker compose cp $resolvedBackup "postgres:$containerFile"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar o backup para validação.' }
    docker compose exec -T postgres dropdb -U gestao_de_funcionarios --if-exists $restoreDatabase
    docker compose exec -T postgres createdb -U gestao_de_funcionarios $restoreDatabase
    docker compose exec -T postgres pg_restore -U gestao_de_funcionarios -d $restoreDatabase $containerFile
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao restaurar o backup descartável.' }
    $migrationCount = docker compose exec -T postgres psql -U gestao_de_funcionarios -d $restoreDatabase -Atc 'select count(*) from alembic_version'
    if ([int]$migrationCount -lt 1) { throw 'Restauração não contém a versão do esquema.' }
}
finally {
    docker compose exec -T postgres dropdb -U gestao_de_funcionarios --if-exists $restoreDatabase | Out-Null
    Pop-Location
}

Write-Output 'Backup restaurado e validado em banco descartável.'
