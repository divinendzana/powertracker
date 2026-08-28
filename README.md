# PowerTracker 🚀

Plateforme de gestion et d'analyse des consommations de carburant pour CAMTEL

## 📋 Vue d'ensemble

- **Stack**: Django (Backend) + React (Frontend) + PostgreSQL + Redis
- **Durée**: 4-5 semaines
- **Deadline**: Vendredi (3 jours initial)

---

## 🛠️ Prérequis

1. **Python 3.10+** installé
2. **PostgreSQL 18** installé (ou Docker)
3. **Node.js 18+** installé
4. **ngrok** installé (pour l'accès depuis l'extérieur)

### Installer ngrok (si pas déjà fait)

```bash
# Sur Windows (PowerShell)
winget install ngrok/ngrok

# Ou télécharger depuis https://ngrok.com/download
```

---

## 📂 Structure du projet

```
powertracker/
├── backend/              # Django API REST
│   ├── core/            # Configuration Django
│   ├── tracker/         # App principale (models, views, serializers)
│   ├── manage.py        # Script Django
│   └── requirements.txt
├── frontend/            # React TypeScript
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├── scripts/            # Scripts utilitaires
│   ├── dev-db-start.ps1
│   └── dev-db-stop.ps1
├── .env                # Variables d'environnement
├── docker-compose.yml
└── README.md
```

---

## 🚀 Démarrage rapide

### 1️⃣ Configuration de la base de données

La base de données PostgreSQL tourne sur le port **5439** avec:
- Base: `powertracker_db`
- Utilisateur: `powertracker_user`
- Port: `5439`

**Pour démarrer la DB:**
```powershell
cd scripts
.\dev-db-start.ps1
```

**Pour arrêter la DB:**
```powershell
cd scripts
.\dev-db-stop.ps1
```

### 2️⃣ Configuration des variables d'environnement

Assurez-vous que `.env` est configuré:
```env
DB_HOST=localhost
DB_PORT=5439
DB_NAME=powertracker_db
DB_USER=powertracker_user
DB_PASSWORD=votre_mot_de_passe
SECRET_KEY=votre_secret_key_aleatoire
DEBUG=True
```

**Générer une SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3️⃣ Démarrage du Backend Django

```bash
# Activer le venv
.venv\Scripts\Activate.ps1

# Installer les dépendances (si nécessaire)
pip install -r backend/requirements.txt

# Migrer la base de données
cd backend
python manage.py migrate

# Créer l'admin (si nécessaire)
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver 0.0.0.0:8000
```

Le backend sera accessible sur: `http://localhost:8000`

### 4️⃣ Démarrage du Frontend React

```bash
# Activer le venv
.venv\Scripts\Activate.ps1

# Installer les dépendances (si nécessaire)
cd frontend
npm install

# Démarrer le serveur
npm run dev
```

Le frontend sera accessible sur: `http://localhost:5173`

---

## 🔗 Accès depuis l'extérieur avec NGROK

### Option 1: Accéder au Backend uniquement

```bash
# 1. Démarrer le backend Django
cd backend
python manage.py runserver 0.0.0.0:8000

# 2. Dans un autre terminal, démarrer ngrok
ngrok http 8000
```

Copiez l'URL HTTPS générée (ex: `https://abc123.ngrok-free.app`)

### Option 2: Accéder au Backend + Frontend (Proxy)

```bash
# 1. Démarrer le frontend React
cd frontend
npm run dev

# 2. Dans un autre terminal, démarrer ngrok avec le proxy
ngrok http 5173
```

Copiez l'URL HTTPS générée.

### Option 3: Accéder à l'application complète (Backend + Frontend)

Créez un fichier `ngrok.yml` dans le racine du projet:

```yaml
tunnels:
  powertracker:
    proto: http
    addr: 8000
    # Pour ngrok avec auth
    # auth: "votre_email:mot_de_passe"
```

Puis:
```bash
# Démarrer le backend
cd backend
python manage.py runserver 0.0.0.0:8000

# Dans un autre terminal
ngrok start powertracker
```

Copiez l'URL HTTPS générée.

---

## 🔐 Comptes de test

### Administratrice
- **Email**: `divine.ndzana@camtel.cm`
- **Password**: `Passw0rd-Secure!`

### Employé
- **PIN**: `2468`

---

## 📊 État du projet

| Étape | Statut | % Complété |
|-------|--------|-----------|
| 0 - Préparation | 🟩 Complété | 100% |
| 1 - Modélisation DB | 🟩 Complété | 100% |
| 2 - Backend Django | 🟨 En cours | 90% |
| 3 - Frontend React | 🟨 En cours | 90% |
| 4 - Notifications | 🟨 En cours | 70% |
| 5 - Tests & Deploy | ⬜ À faire | 0% |

### Problèmes connus
- 1 test échouant: `test_employee_autre_site_ne_voit_pas_la_coupure_404` → retourne 403 au lieu de 404 (problème de permission)

---

## 🧪 Tests

```bash
# Activer le venv
.venv\Scripts\Activate.ps1

# Tous les tests
cd backend
python manage.py test tracker --noinput

# Tests spécifiques
python manage.py test tracker.tests.CoupuresApiTests --noinput
python manage.py test tracker.tests.EmployeApiTests --noinput
python manage.py test tracker.tests.PermissionsApiTests --noinput
```

---

## 📝 API Endpoints

### Authentification
- `POST /api/auth/login/` - Connexion administratrice
- `POST /api/auth/pin/` - Connexion employé

### Sites
- `GET /api/sites/` - Liste des sites
- `POST /api/sites/` - Créer un site (Admin)

### Coupures
- `GET /api/coupures/` - Liste des coupures
- `POST /api/coupures/` - Créer une coupure
- `PATCH /api/coupures/{id}/close/` - Fermer une coupure
- `GET /api/coupures/{id}/` - Détails d'une coupure

### Sessions Groupe
- `GET /api/sessions-groupe/` - Liste des sessions
- `POST /api/sessions-groupe/` - Démarrer une session
- `PATCH /api/sessions-groupe/{id}/stop/` - Arrêter une session

### Pleins de carburant
- `GET /api/pleins-carburant/` - Liste des pleins
- `POST /api/pleins-carburant/` - Enregistrer un plein

### Alertes
- `GET /api/alertes/` - Liste des alertes
- `PATCH /api/alertes/{id}/resolve/` - Résoudre une alerte

### Dashboard
- `GET /api/dashboard/` - Vue d'ensemble
- `GET /api/historique-mensuel/` - Historique mensuel

---

## 🛠️ Scripts disponibles

```powershell
# Scripts de base de données
cd scripts
.\dev-db-start.ps1    # Démarrer PostgreSQL
.\dev-db-stop.ps1     # Arrêter PostgreSQL

# Scripts de démarrage de l'application
.\start-app.ps1       # Démarrer tout (DB + Backend + Frontend + Ngrok)
.\stop-app.ps1        # Arrêter tout

# Scripts Docker (quand Docker est disponible)
docker-compose up -d   # Démarrer tout
docker-compose down    # Arrêter tout
```

---

## 📚 Documentation

- **GEMINI.md** - Roadmap interactive avec Gemini
- **QUICK_START.md** - Guide de démarrage rapide
- **requirements.txt** - Dépendances Python
- **frontend/package.json** - Dépendances Node.js

---

## 🎯 Prochaines étapes

1. Corriger le test `test_employee_autre_site_ne_voit_pas_la_coupure_404`
2. Compléter le frontend React
3. Implémenter les notifications Telegram
4. Déployer en production

---

**Créé le**: 27/08/2026  
**Dernière mise à jour**: 27/08/2026  
**Statut global**: 🟨 En cours
