$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$workspace = (Resolve-Path (Join-Path $root '..')).Path
$destination = Join-Path $workspace ("_INITIALIZER_PROOF_" + [guid]::NewGuid().ToString('N'))
$initializer = Join-Path $root 'scripts\new-saas.ps1'

try {
    $demonstrationName = 'SaaS Demonstra' + [char]0x00E7 + [char]0x00E3 + 'o'
    & $initializer -Name $demonstrationName -Destination $destination
    foreach ($required in @(
        'README.md',
        'PROJETO.md',
        'compose.yaml',
        '.env.example',
        '.template-origin.json',
        'docs\PROJECT_PIPELINE.md',
        'docs\PROMPT_MESTRE_NOVO_SAAS.md',
        'docs_referencias\contexto_atual.md',
        'docs_referencias\requisitos.md'
    )) {
        if (-not (Test-Path -LiteralPath (Join-Path $destination $required))) {
            throw "Cópia sem arquivo obrigatório: $required"
        }
    }
    $forbidden = @('.git', '.env', '.venv', 'node_modules', '.pytest_cache', '.pytest-tmp', 'uploads', 'dist')
    foreach ($name in $forbidden) {
        $found = Get-ChildItem -LiteralPath $destination -Force -Recurse -Directory -ErrorAction SilentlyContinue |
            Where-Object Name -eq $name | Select-Object -First 1
        if ($found) { throw "Artefato proibido copiado: $($found.FullName)" }
    }
    $origin = Get-Content -Raw -LiteralPath (Join-Path $destination '.template-origin.json') | ConvertFrom-Json
    if ($origin.baseVersion -ne 'V1') { throw 'Linhagem V1 ausente.' }
    if ($origin.projectName -ne $demonstrationName) { throw 'Nome do projeto incorreto.' }
    if ($origin.automaticUpdates -ne $false) { throw 'Política de atualização incorreta.' }
    $environment = Get-Content -Raw -LiteralPath (Join-Path $destination '.env.example')
    foreach ($key in @('API_PORT=', 'WEB_PORT=', 'POSTGRES_PORT=', 'REDIS_PORT=')) {
        if (-not $environment.Contains($key)) { throw "Porta sugerida ausente: $key" }
    }
    $generatedDatabase = 'saas_demonstracao'
    $generatedAppRole = "${generatedDatabase}_app"
    $operationalFiles = @(
        'compose.yaml',
        'infra\postgres\init-app-role.sql',
        'scripts\backup.ps1',
        'scripts\verify.ps1',
        'scripts\restore-check.ps1',
        'scripts\migration-fresh-check.ps1',
        'tests\smoke\compose-health.ps1',
        'backend\pyproject.toml',
        'backend\app\core\config.py',
        'backend\tests\integration\auth_support.py',
        'backend\tests\security\test_login_rate_limit.py',
        'backend\tests\integration\test_logout_flow.py',
        'backend\tests\integration\test_auth_flow.py',
        'backend\tests\integration\test_audit_lgpd_schema.py',
        'frontend\package.json',
        'frontend\package-lock.json'
    )
    $operationalFiles += Get-ChildItem -LiteralPath (Join-Path $destination 'backend\migrations\versions') -Filter '*.py' |
        ForEach-Object { 'backend\migrations\versions\' + $_.Name }
    foreach ($relativePath in $operationalFiles) {
        $content = Get-Content -Raw -LiteralPath (Join-Path $destination $relativePath)
        if ($content -match 'base_saas|base-saas|localhost:5432|localhost:6379') {
            throw "Identidade operacional da Base vazou para: $relativePath"
        }
    }
    $roleSql = Get-Content -Raw -LiteralPath (Join-Path $destination 'infra\postgres\init-app-role.sql')
    if (-not $roleSql.Contains($generatedAppRole) -or -not $roleSql.Contains($generatedDatabase)) {
        throw 'Banco e papel de aplicação da cópia não foram personalizados.'
    }
    $backendPackage = Get-Content -Raw -LiteralPath (Join-Path $destination 'backend\pyproject.toml')
    $frontendPackage = Get-Content -Raw -LiteralPath (Join-Path $destination 'frontend\package.json')
    if (-not $backendPackage.Contains('saas-demonstracao-backend')) { throw 'Pacote backend não foi personalizado.' }
    if (-not $frontendPackage.Contains('saas-demonstracao-frontend')) { throw 'Pacote frontend não foi personalizado.' }
    $healthTest = Get-Content -Raw -LiteralPath (Join-Path $destination 'backend\tests\api\test_health.py')
    if (-not $healthTest.Contains("'service': '$demonstrationName'")) {
        throw 'Contrato de saúde ainda usa o nome da Base.'
    }
    & (Join-Path $destination 'tests\smoke\test_template_hygiene.ps1')
    Push-Location $destination
    try {
        docker compose --env-file .env.example config --quiet
        if ($LASTEXITCODE -ne 0) { throw 'Compose da cópia gerada é inválido.' }
    }
    finally { Pop-Location }
    try {
        & $initializer -Name 'Não sobrescrever' -Destination $destination
        throw 'Inicializador aceitou destino existente.'
    }
    catch {
        if ($_.Exception.Message -notmatch 'já existe') { throw }
    }
}
finally {
    $resolvedWorkspace = [System.IO.Path]::GetFullPath($workspace)
    $resolvedDestination = [System.IO.Path]::GetFullPath($destination)
    if ($resolvedDestination.StartsWith($resolvedWorkspace, [System.StringComparison]::OrdinalIgnoreCase) -and
        (Split-Path -Leaf $resolvedDestination).StartsWith('_INITIALIZER_PROOF_') -and
        (Test-Path -LiteralPath $resolvedDestination)) {
        Remove-Item -LiteralPath $resolvedDestination -Recurse -Force
    }
}

Write-Host 'Inicializador criou uma cópia limpa e independente.'
