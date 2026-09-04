$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$checkScript = Join-Path $projectRoot 'scripts\migration-fresh-check.ps1'

$result = & $checkScript
if ($LASTEXITCODE -ne 0) { throw 'A prova de migrations em banco vazio falhou.' }
if ($result -notcontains 'Migrations aprovadas em banco vazio descartável.') {
    throw 'A prova não confirmou a aplicação completa das migrations.'
}

Write-Output 'Smoke de banco vazio aprovado.'
