#!/usr/bin/env pwsh
# Script pour démarrer l'application PowerTracker avec ngrok

Write-Host "🚀 Démarrage de PowerTracker..." -ForegroundColor Cyan

# 1. Démarrer la base de données
Write-Host "`n📊 Démarrage de PostgreSQL..." -ForegroundColor Yellow
cd scripts
.\dev-db-start.ps1
Start-Sleep -Seconds 3

# 2. Vérifier le venv et installer les dépendances
Write-Host "`n📦 Vérification du venv..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Le venv n'existe pas. Création en cours..." -ForegroundColor Red
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r backend\requirements.txt
} else {
    .venv\Scripts\Activate.ps1
}

# 3. Migrer la base de données
Write-Host "`n🗄️ Migration de la base de données..." -ForegroundColor Yellow
cd backend
python manage.py migrate --noinput

# 4. Démarrer le serveur Django
Write-Host "`n⚙️ Démarrage du backend Django..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "manage.py", "runserver", "0.0.0.0:8000" -WindowStyle Normal

# 5. Démarrer le frontend React
Write-Host "`n⚛️ Démarrage du frontend React..." -ForegroundColor Green
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Normal

# 6. Démarrer ngrok
Write-Host "`n🔗 Démarrage de ngrok..." -ForegroundColor Yellow
Start-Process -FilePath "ngrok" -ArgumentList "start", "powertracker" -WindowStyle Normal

Write-Host "`n✅ Application démarrée !" -ForegroundColor Green
Write-Host "`n📍 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "`n🌐 Ngrok URL: https://<votre-ngrok-url>.ngrok-free.app" -ForegroundColor Cyan
Write-Host "`n💡 Appuyez sur Ctrl+C pour arrêter tout" -ForegroundColor Gray
