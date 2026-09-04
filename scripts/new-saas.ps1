param(
    [Parameter(Mandatory = $true)]
    [ValidateLength(2, 80)]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [string]$Destination
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$destinationPath = [System.IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $destinationPath) {
    throw "O destino já existe e não será sobrescrito: $destinationPath"
}

$decomposed = $Name.Normalize([Text.NormalizationForm]::FormD)
$letters = foreach ($character in $decomposed.ToCharArray()) {
    if ([Globalization.CharUnicodeInfo]::GetUnicodeCategory($character) -ne
        [Globalization.UnicodeCategory]::NonSpacingMark) { $character }
}
$slug = ((-join $letters).ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
if (-not $slug) { throw 'O nome precisa gerar um identificador técnico válido.' }
$databaseName = $slug.Replace('-', '_')

$sha = [Security.Cryptography.SHA256]::Create()
try {
    $hash = $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($slug))
}
finally {
    $sha.Dispose()
}
$offset = [BitConverter]::ToUInt32($hash, 0) % 800
$ports = @{
    Api = 10000 + $offset
    Web = 11000 + $offset
    Postgres = 12000 + $offset
    Redis = 13000 + $offset
    MailpitWeb = 14000 + $offset
    MailpitSmtp = 15000 + $offset
}

$excludedDirectories = @(
    '.git', '.venv', '.poetry-cache', 'node_modules', 'dist', '__pycache__',
    '.pytest_cache', '.pytest-tmp', '.ruff_cache', '.mypy_cache', 'htmlcov',
    'uploads', 'backups', '.codex', '.claude', '.agents'
)
$copyArguments = @(
    $source, $destinationPath, '/E', '/R:1', '/W:1', '/NFL', '/NDL', '/NJH', '/NJS',
    '/XD'
) + $excludedDirectories + @('/XF', '.env', '.env.*', '*.sqlite', '*.sqlite3', '*.db', '*.dump', '*.bak')
& robocopy @copyArguments | Out-Null
if ($LASTEXITCODE -gt 7) { throw "Falha ao copiar a Base SaaS (robocopy $LASTEXITCODE)." }

$environmentPath = Join-Path $destinationPath '.env.example'
Copy-Item -LiteralPath (Join-Path $source '.env.example') -Destination $environmentPath
$environment = Get-Content -Raw -LiteralPath $environmentPath
$environment = $environment.Replace('APP_NAME=Base SaaS V1', "APP_NAME=$Name")
$environment = $environment.Replace('API_PORT=8000', "API_PORT=$($ports.Api)")
$environment = $environment.Replace('WEB_PORT=5173', "WEB_PORT=$($ports.Web)")
$environment = $environment.Replace('POSTGRES_PORT=5432', "POSTGRES_PORT=$($ports.Postgres)")
$environment = $environment.Replace('REDIS_PORT=6379', "REDIS_PORT=$($ports.Redis)")
$environment = $environment.Replace('MAILPIT_WEB_PORT=8025', "MAILPIT_WEB_PORT=$($ports.MailpitWeb)")
$environment = $environment.Replace('MAILPIT_SMTP_PORT=1025', "MAILPIT_SMTP_PORT=$($ports.MailpitSmtp)")
$environment = $environment.Replace('base_saas_app', "${databaseName}_app")
$environment = $environment.Replace('base_saas', $databaseName)
$environment = $environment.Replace('http://localhost:5173', "http://localhost:$($ports.Web)")
Set-Content -LiteralPath $environmentPath -Value $environment -Encoding utf8

$composePath = Join-Path $destinationPath 'compose.yaml'
$compose = Get-Content -Raw -LiteralPath $composePath
$compose = $compose.Replace('name: base-saas-v1', "name: $slug")
Set-Content -LiteralPath $composePath -Value $compose -Encoding utf8

# Personaliza somente arquivos operacionais conhecidos. Documentação histórica e
# planos da Base permanecem intactos para preservar a rastreabilidade da origem.
$operationalPaths = @(
    (Join-Path $destinationPath 'infra\postgres\init-app-role.sql'),
    (Join-Path $destinationPath 'scripts\backup.ps1'),
    (Join-Path $destinationPath 'scripts\verify.ps1'),
    (Join-Path $destinationPath 'scripts\restore-check.ps1'),
    (Join-Path $destinationPath 'scripts\migration-fresh-check.ps1'),
    (Join-Path $destinationPath 'tests\smoke\compose-health.ps1'),
    (Join-Path $destinationPath 'backend\pyproject.toml'),
    (Join-Path $destinationPath 'backend\app\core\config.py'),
    (Join-Path $destinationPath 'frontend\package.json'),
    (Join-Path $destinationPath 'frontend\package-lock.json')
)
$operationalPaths += Get-ChildItem -LiteralPath (Join-Path $destinationPath 'backend\migrations\versions') -Filter '*.py' |
    Select-Object -ExpandProperty FullName
$operationalPaths += Get-ChildItem -LiteralPath (Join-Path $destinationPath 'backend\tests') -Filter '*.py' -Recurse |
    Select-Object -ExpandProperty FullName

foreach ($path in $operationalPaths | Select-Object -Unique) {
    $content = Get-Content -Raw -LiteralPath $path
    $content = $content.Replace('base_saas_app', "${databaseName}_app")
    $content = $content.Replace('base_saas', $databaseName)
    $content = $content.Replace('base-saas-backend', "$slug-backend")
    $content = $content.Replace('base-saas-frontend', "$slug-frontend")
    $content = $content.Replace('base-saas-pytest', "$slug-pytest")
    $content = $content.Replace('localhost:5432', "localhost:$($ports.Postgres)")
    $content = $content.Replace('localhost:6379', "localhost:$($ports.Redis)")
    $content = $content.Replace('localhost:5173', "localhost:$($ports.Web)")
    $content = $content.Replace('localhost:8000', "localhost:$($ports.Api)")
    $content = $content.Replace('localhost:8025', "localhost:$($ports.MailpitWeb)")
    $content = $content.Replace('Base SaaS V1', $Name)
    Set-Content -LiteralPath $path -Value $content -Encoding utf8
}

$readmePath = Join-Path $destinationPath 'README.md'
$readme = (Get-Content -Raw -LiteralPath $readmePath).Replace('# Base SaaS V1', "# $Name")
Set-Content -LiteralPath $readmePath -Value $readme -Encoding utf8

$lineagePath = Join-Path $destinationPath 'docs\BASE_LINEAGE.md'
$lineage = @"
# Linhagem da Base

- Projeto: $Name
- Identificador técnico: $slug
- Template de origem: Base SaaS V1
- Versão de origem: V1
- Criado em: $(Get-Date -Format 'yyyy-MM-dd')
- Política de atualização: sem atualização automática

Este projeto é uma cópia independente. Uma futura Base V2 não o sobrescreve.
Melhorias exigem análise de impacto, backup, migration, testes e reversão próprios.
"@
Set-Content -LiteralPath $lineagePath -Value $lineage -Encoding utf8

$manifest = [ordered]@{
    projectName = $Name
    technicalId = $slug
    baseName = 'Base SaaS'
    baseVersion = 'V1'
    createdAt = (Get-Date).ToUniversalTime().ToString('o')
    automaticUpdates = $false
    suggestedPorts = $ports
}
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $destinationPath '.template-origin.json') -Encoding utf8

Write-Host "Projeto criado em: $destinationPath"
Write-Host "Identificador: $slug | API: $($ports.Api) | Web: $($ports.Web)"
