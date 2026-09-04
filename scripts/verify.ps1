$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$env:APP_ENV = 'test'
$env:DATABASE_URL = 'postgresql+asyncpg://gestao_de_funcionarios_app:local_app_only_change_me@localhost:12547/gestao_de_funcionarios'
$env:MIGRATION_DATABASE_URL = 'postgresql+asyncpg://gestao_de_funcionarios:local_only_change_me@localhost:12547/gestao_de_funcionarios'
$env:REDIS_URL = 'redis://localhost:13547/0'

& powershell -ExecutionPolicy Bypass -File (Join-Path $root 'tests/smoke/test_template_hygiene.ps1')

Push-Location (Join-Path $root 'backend')
try {
    $pytestTemp = Join-Path $env:TEMP "gestao-de-funcionarios-pytest-$PID"
    & .\.venv\Scripts\ruff.exe check .
    if ($LASTEXITCODE -ne 0) { throw 'Ruff falhou' }
    & .\.venv\Scripts\mypy.exe app
    if ($LASTEXITCODE -ne 0) { throw 'mypy falhou' }
    & .\.venv\Scripts\python.exe -m pytest -q --basetemp=$pytestTemp -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw 'Pytest falhou' }
} finally { Pop-Location }

Push-Location (Join-Path $root 'frontend')
try {
    & npm run lint
    if ($LASTEXITCODE -ne 0) { throw 'ESLint falhou' }
    & npm run typecheck
    if ($LASTEXITCODE -ne 0) { throw 'TypeScript falhou' }
    & npm test -- --run
    if ($LASTEXITCODE -ne 0) { throw 'Vitest falhou' }
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Build do frontend falhou' }
} finally { Pop-Location }

Write-Host 'Verificação local completa: APROVADA.'
