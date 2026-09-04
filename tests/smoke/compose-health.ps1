$ErrorActionPreference = 'Stop'

$api = Invoke-RestMethod -Uri 'http://localhost:10547/api/v1/health/services' -TimeoutSec 10
if ($api.status -ne 'ok') { throw 'API não está saudável' }

$web = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:11547' -TimeoutSec 10
if ($web.StatusCode -ne 200) { throw 'Frontend não respondeu 200' }

$mailpit = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:14547/api/v1/info' -TimeoutSec 10
if ($mailpit.StatusCode -ne 200) { throw 'Mailpit não está saudável' }

$runningServices = @(docker compose ps --status running --services)
if ($LASTEXITCODE -ne 0 -or $runningServices -notcontains 'worker') {
    throw 'Worker não está em execução'
}

Write-Host 'API, worker, frontend, PostgreSQL, Redis e Mailpit estão operacionais.'
