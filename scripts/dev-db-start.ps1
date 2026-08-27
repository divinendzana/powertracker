# Démarre l'instance PostgreSQL de développement du projet PowerTracker (port 5439)
# Usage : .\scripts\dev-db-start.ps1
$bin = 'C:\Program Files\PostgreSQL\18\bin'
$dataDir = Resolve-Path (Join-Path $PSScriptRoot '..\.pgdata')
& "$bin\pg_ctl.exe" -D $dataDir -l (Join-Path $dataDir 'server.log') -o '-p 5439' start