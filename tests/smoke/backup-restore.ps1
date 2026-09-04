$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$backupScript = Join-Path $projectRoot 'scripts\backup.ps1'
$restoreScript = Join-Path $projectRoot 'scripts\restore-check.ps1'
$backupFile = [System.IO.Path]::GetTempFileName()
$checksumFile = "$backupFile.sha256"

try {
    & $backupScript -BackupFile $backupFile
    if (-not (Test-Path -LiteralPath $backupFile)) { throw 'Backup não foi criado.' }
    if (-not (Test-Path -LiteralPath $checksumFile)) { throw 'Checksum não foi criado.' }
    & $restoreScript -BackupFile $backupFile
}
finally {
    if (Test-Path -LiteralPath $backupFile) { Remove-Item -LiteralPath $backupFile -Force }
    if (Test-Path -LiteralPath $checksumFile) { Remove-Item -LiteralPath $checksumFile -Force }
}
