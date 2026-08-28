#!/usr/bin/env pwsh
# Script pour arrêter l'application PowerTracker

Write-Host "🛑 Arrêt de PowerTracker..." -ForegroundColor Cyan

# 1. Arrêter la base de données
Write-Host "`n📊 Arrêt de PostgreSQL..." -ForegroundColor Yellow
cd scripts
.\dev-db-stop.ps1

# 2. Trouver et tuer les processus ngrok
Write-Host "`n🔗 Arrêt de ngrok..." -ForegroundColor Yellow
$ngrokProcesses = Get-Process -Name ngrok -ErrorAction SilentlyContinue
if ($ngrokProcesses) {
    foreach ($proc in $ngrokProcesses) {
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "✅ Ngrok arrêté" -ForegroundColor Green
}

# 3. Trouver et tuer les processus Django
Write-Host "`n⚙️ Arrêt du backend Django..." -ForegroundColor Yellow
$djangoProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*manage.py runserver*" }
if ($djangoProcesses) {
    foreach ($proc in $djangoProcesses) {
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "✅ Backend arrêté" -ForegroundColor Green
}

# 4. Trouver et tuer les processus React/npm
Write-Host "`n⚛️ Arrêt du frontend React..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
if ($nodeProcesses) {
    foreach ($proc in $nodeProcesses) {
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "✅ Frontend arrêté" -ForegroundColor Green
}

Write-Host "`n✅ Application complètement arrêtée" -ForegroundColor Green
