$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$required = @('.gitignore', '.env.example', '.dockerignore', 'README.md', 'compose.yaml')

foreach ($name in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $name))) {
        throw "Arquivo obrigatório ausente: $name"
    }
}

$ignore = Get-Content -LiteralPath (Join-Path $root '.gitignore') -Raw
$requiredIgnoreRules = @(
    '.env', '.git/', '.codex/', '.claude/', '.agents/', '.venv/', '.poetry-cache/', '.virtualenv-cache/',
    'node_modules/', 'dist/', 'uploads/', 'backups/', '*.dump'
)
foreach ($rule in $requiredIgnoreRules) {
    if (-not $ignore.Contains($rule)) { throw "Proteção ausente no .gitignore: $rule" }
}

$secretPatterns = @('*.pem', '*.p12', '*.key')
foreach ($pattern in $secretPatterns) {
    $found = Get-ChildItem -LiteralPath $root -File -Recurse -Filter $pattern -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\node_modules\\|\\.venv\\|\\.poetry-cache\\|\\.virtualenv-cache\\' } |
        Select-Object -First 1
    if ($found) { throw "Possível segredo no template: $($found.FullName)" }
}

Write-Host 'Contrato e proteções do template estão corretos.'
