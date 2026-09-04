param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$resolvedParent = (Resolve-Path (Split-Path -Parent $BackupFile)).Path
$resolvedBackup = Join-Path $resolvedParent (Split-Path -Leaf $BackupFile)
$containerFile = '/tmp/gestao_de_funcionarios_backup.dump'

Push-Location $projectRoot
try {
    docker compose exec -T postgres pg_dump -U gestao_de_funcionarios -d gestao_de_funcionarios -Fc --file=$containerFile
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao gerar o dump PostgreSQL.' }
    docker compose cp "postgres:$containerFile" $resolvedBackup
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar o dump PostgreSQL.' }
    (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedBackup).Hash.ToLowerInvariant() |
        Set-Content -Encoding ascii -NoNewline -LiteralPath "$resolvedBackup.sha256"
}
finally {
    Pop-Location
}

Write-Output $resolvedBackup
