# Arrête l'instance PostgreSQL de développement du projet PowerTracker
# Usage : .\scripts\dev-db-stop.ps1
$bin = 'C:\Program Files\PostgreSQL\18\bin'
$dataDir = Resolve-Path (Join-Path $PSScriptRoot '..\.pgdata')
& "$bin\pg_ctl.exe" -D $dataDir stop -m fast