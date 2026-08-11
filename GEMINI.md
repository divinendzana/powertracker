# 🚀 GEMINI.md - Roadmap du Projet CAMTEL avec Gemini

**Plateforme de Gestion et d'Analyse des Consommations de Carburant**

---

## 📋 Vue d'ensemble du projet

**Durée totale**: 4-5 semaines  
**Deadline**: Vendredi (3 jours initial)  
**Stack**: Django (Backend) + React (Frontend) + PostgreSQL  
**Notifications**: Telegram Bot / SMS

---

## ✅ Système de Suivi

| Étape | Statut | % Complété | Dernière MAJ |
|-------|--------|-----------|--------------|
| Étape 0 - Préparation | ⬜ À faire | 0% | - |
| Étape 1 - Modélisation DB | ⬜ À faire | 0% | - |
| Étape 2 - Backend Django | ⬜ À faire | 0% | - |
| Étape 3 - Frontend React | ⬜ À faire | 0% | - |
| Étape 4 - Notifications | ⬜ À faire | 0% | - |
| Étape 5 - Tests & Deploy | ⬜ À faire | 0% | - |

**Légende**: ⬜ À faire | 🟨 En cours | 🟩 Complété | ❌ Bloqué

---

## 🎯 ÉTAPE 0 - PRÉPARATION (1-2 jours)

### Objectif
Mettre en place l'infrastructure de développement et initialiser le projet

### Tâches
- [ ] Créer le dépôt GitHub avec structure `backend/` et `frontend/`
- [ ] Installer PostgreSQL localement ou via Docker
- [ ] Définir les rôles utilisateurs (Admin, Employé)
- [ ] Créer les fichiers `.env` pour les configurations

### 📝 Prompts Gemini

**Prompt 1 - Structure du projet**
```
Aide-moi à créer une structure de projet Django + React optimale pour une plateforme 
de gestion de carburant. Je veux :
- Un backend Django avec Django REST Framework
- Un frontend React avec TypeScript
- Docker Compose pour la base de données PostgreSQL
- Variables d'environnement correctement configurées

Génère:
1. La structure de dossiers complète
2. Les fichiers de configuration essentiels (.env, .gitignore, docker-compose.yml)
3. Les requirements.txt et package.json de base
```

**Prompt 2 - Authentification JWT + PIN**
```
Je dois implémenter deux systèmes d'authentification :
1. JWT pour l'admin (Django)
2. PIN simple pour les employés

Fournis le code Django pour :
- Modèle Employee avec champ PIN
- Endpoint /api/auth/jwt/ pour admin
- Endpoint /api/auth/pin/ pour employés
- Middleware de vérification JWT
```

### ✍️ Notes & Observations

---

## 🎯 ÉTAPE 1 - MODÉLISATION DE LA BASE DE DONNÉES (2-3 jours)

### Objectif
Concevoir et implémenter le schéma PostgreSQL avec 7 tables principales

### Tables à créer
1. **sites** - Maison, Restaurant
2. **employees** - Nom, Code PIN, Site associé, Score fiabilité
3. **coupures** - Site, Début, Fin, Déclaré par, Durée calculée
4. **groupe_sessions** - Site, Employé, Démarrage, Arrêt, Durée
5. **pleins_carburant** - Site, Litres, Prix, Date, Employé
6. **consommation_electricite** - Site, Mois, kWh/Montant, Date
7. **alertes** - Type, Site, Message, Date, Résolue (bool)

### Tâches
- [ ] Créer le schéma SQL complet
- [ ] Générer les modèles Django à partir du schéma
- [ ] Configurer les relations (ForeignKey, ManyToMany)
- [ ] Créer les migrations Django
- [ ] Tester les migrations en local

### 📝 Prompts Gemini

**Prompt 3 - Schéma SQL complet**
```
Génère le schéma SQL PostgreSQL complet pour une plateforme de gestion de carburant
avec ces 7 tables:

Tables:
- sites (id, nom, adresse, type)
- employees (id, nom, code_pin, site_id, score_fiabilite)
- coupures (id, site_id, debut, fin, declare_par_id, duree_calculee)
- groupe_sessions (id, site_id, employe_id, demarrage, arret, duree_calculee)
- pleins_carburant (id, site_id, litres, prix, date, employe_id)
- consommation_electricite (id, site_id, mois, kwh_ou_montant, date)
- alertes (id, type, site_id, message, date, resolue)

Inclus:
- Primary keys
- Foreign keys
- Indexes sur les colonnes fréquemment filtrées
- Contraintes appropriées
- Types de données optimisés
```

**Prompt 4 - Modèles Django**
```
Convertis ce schéma SQL en modèles Django (models.py):

[INSÉRER LE SCHÉMA SQL ICI]

Génère:
1. Tous les modèles Django avec Meta options
2. Les champs avec leurs types appropriés
3. Les validateurs si nécessaire
4. Les __str__ methods
5. Les custom managers si utile
```

### ✍️ Notes & Observations

---

## 🎯 ÉTAPE 2 - BACKEND DJANGO (5-7 jours)

### Objectif
Développer l'API REST complète avec la logique métier

### Endpoints à implémenter
- `POST /api/coupures/` - Déclarer une coupure
- `POST /api/groupe/demarrer/` - Démarrer groupe électrogène
- `POST /api/groupe/arreter/` - Arrêter groupe électrogène
- `POST /api/carburant/` - Enregistrer un plein
- `GET /api/dashboard/` - Stats consolidées
- `GET /api/alertes/` - Récupérer les alertes

### Logique métier clé
1. **Détection d'écart carburant**: Chaque plein → calculer ratio L/h → comparer à la moyenne
2. **Détection anomalie électricité**: Job planifié → comparer conso mois courant vs précédents

### Tâches
- [ ] Créer les serializers Django
- [ ] Implémenter les endpoints CRUD
- [ ] Ajouter les validations personnalisées
- [ ] Implémenter la logique de détection d'écart
- [ ] Mettre en place le job de comparaison électricité
- [ ] Tester les endpoints avec Postman/Insomnia

### 📝 Prompts Gemini

**Prompt 5 - Serializers Django REST**
```
Crée les serializers Django REST pour ces modèles:
- Site
- Employee
- Coupure
- GroupeSession
- PleinCarburant
- ConsommationElectricite
- Alerte

Pour chaque serializer:
1. Inclus tous les champs pertinents
2. Ajoute des validations spécifiques
3. Crée des nested serializers si nécessaire
4. Ajoute des champs read-only calculés si pertinent
```

**Prompt 6 - Logique de détection d'écart carburant**
```
J'ai besoin d'une logique qui:
1. Chaque fois qu'un plein carburant est enregistré
2. Calcule le ratio L/h attendu (moyenne historique de tous les pleins précédents)
3. Extrait le ratio déclaré du nouveau plein
4. Si écart > 20%, créer une alerte automatiquement

Le code doit:
- Gérer le cas où il n'y a pas de pleins antérieurs
- Utiliser Django signals pour déclencher automatiquement
- Créer une Alerte avec message descriptif

Fournis le code Django complet avec signal, fonction de calcul, et création d'Alerte.
```

**Prompt 7 - Job de comparaison électricité**
```
Crée un job Django planifié qui:
1. S'exécute chaque mois (ou toutes les semaines pour test)
2. Récupère la consommation électrique du mois courant
3. La compare aux 3 mois précédents
4. Déclenche une alerte si incohérence (ex: +50% soudain)

Utilise Django APScheduler ou une simple commande manage.py.
Fournis:
- La structure du job
- La logique de comparaison
- La création d'Alerte si anomalie détectée
```

**Prompt 8 - ViewSets et Endpoints**
```
Crée les ViewSets Django REST Framework pour:
- SiteViewSet (CRUD complet)
- EmployeeViewSet (CRUD complet, sans exposer les PIN)
- CoupureViewSet (Créer, lister, récupérer)
- GroupeSessionViewSet (POST demarrer/arreter, lister)
- PleinCarburantViewSet (Créer, lister)
- AlerteViewSet (Récupérer, lister, marquer comme résolue)

Ajoute:
- Filtrage par site
- Pagination
- Permissions (authentification requise)
- Métadonnées appropriées (docstrings)
```

### ✍️ Notes & Observations

---

## 🎯 ÉTAPE 3 - FRONTEND REACT (5-7 jours)

### Objectif
Développer l'interface utilisateur interactive et responsive

### Écrans à créer
1. **Login** - Admin (JWT)
2. **Déclarer Coupure** - Boutons Démarrer/Arrêter
3. **Groupe Électrogène** - Sélection employé + PIN
4. **Dashboard Principal** - KPIs et alertes
5. **Vue Historique** - Comparaison mois par mois

### Tâches
- [ ] Créer la structure du projet React
- [ ] Implémenter l'authentification JWT
- [ ] Créer l'écran de login
- [ ] Développer le dashboard avec graphiques
- [ ] Implémenter les modales de déclaration
- [ ] Ajouter la gestion des alertes
- [ ] Tester la responsivité

### 📝 Prompts Gemini

**Prompt 9 - Structure React + TypeScript**
```
Crée une structure de projet React moderne avec TypeScript pour une plateforme
de gestion de carburant. 

Besoins:
- Authentification JWT
- Routing avec React Router v6
- Gestion d'état avec Redux Toolkit ou Zustand
- Composants réutilisables
- Styles avec Tailwind CSS ou Material-UI
- API client (axios)

Fournis:
1. Structure de dossiers complète
2. Configuration TypeScript
3. Package.json avec les dépendances
4. Layout/Template de base
```

**Prompt 10 - Écran de login**
```
Crée un écran de login React pour un admin avec:
- Email/Mot de passe
- Validation côté client
- Appel API /api/auth/jwt/
- Stockage du JWT en localStorage
- Redirection vers dashboard après connexion
- Gestion des erreurs

Utilise:
- React Hook Form pour les formulaires
- TypeScript
- Tailwind CSS
- Axios pour l'API
```

**Prompt 11 - Dashboard principal**
```
Crée le dashboard avec:
1. Résumé des coupures (par site, temps total)
2. Résumé carburant (litres consommés, coût)
3. Alertes actives (tableau avec statut)
4. Score fiabilité des employés
5. Graphiques: 
   - Consommation carburant par site
   - Heures de coupure par site
   - Tendance alertes par semaine

Utilise:
- Recharts ou Chart.js pour les graphiques
- Tableau avec tri/filtrage
- Refresh automatique chaque minute
```

**Prompt 12 - Écran de déclaration de coupure**
```
Crée un écran simple pour déclarer une coupure avec:
1. Sélection du site (dropdown)
2. Deux boutons: "Démarrer" et "Arrêter"
3. Affichage du statut actuel (en cours, arrêtée)
4. Historique des coupures du jour
5. Confirmation avant action

Le flux:
- Clic "Démarrer" → POST /api/coupures/ {site_id, debut: now}
- Clic "Arrêter" → PATCH /api/coupures/{id} {fin: now}
- Affichage de la durée calculée

Utilise React, TypeScript, Axios
```

**Prompt 13 - Vue historique et comparaison**
```
Crée une vue mensuelle/historique avec:
1. Sélecteur de mois (dropdown ou calendrier)
2. Choisir 2 mois pour comparaison (ex: juin vs juillet)
3. Tableaux comparatifs:
   - Heures coupure
   - Litres carburant
   - Coût total
   - Nombre d'alertes
4. Graphique de tendance (3-6 derniers mois)
5. Écart en pourcentage entre les 2 mois

Utilise:
- Recharts pour les graphiques
- Flexibilité pour choisir les mois
- Export en CSV/PDF (optionnel)
```

### ✍️ Notes & Observations

---

## 🎯 ÉTAPE 4 - NOTIFICATIONS (2-3 jours)

### Objectif
Implémenter un système d'alertes en temps réel

### Canaux de notification
- **Telegram Bot** (recommandé - facile, gratuit)
- **SMS** via Twilio (alternative)

### Tâches
- [ ] Créer un bot Telegram
- [ ] Implémenter l'intégration Django
- [ ] Tester les notifications
- [ ] (Optionnel) Ajouter SMS Twilio

### 📝 Prompts Gemini

**Prompt 14 - Bot Telegram Django**
```
Intègre un bot Telegram à Django pour envoyer des notifications automatiques.

Requirements:
1. Quand une Alerte est créée → envoyer message Telegram
2. Format du message: 
   "🚨 Alerte: [Type] - [Message] pour site [Site]"
3. Stocker le chat_id de l'admin
4. Gérer les erreurs de connexion

Fournis:
1. Modèle AlerteNotification (stocker qui a reçu la notif)
2. Service de notification Telegram
3. Signal Django pour déclencher automatiquement
4. Configuration des variables d'env
5. Instructions pour créer le bot et obtenir le token
```

**Prompt 15 - SMS Twilio (optionnel)**
```
Ajoute une option SMS via Twilio comme fallback:
1. Configuration Twilio (accountSid, authToken, phone)
2. Service qui envoie SMS si Telegram échoue
3. Logging des SMS envoyés
4. Rate limiting (max 1 SMS par alerte)

Code Django avec Twilio SDK
```

### ✍️ Notes & Observations

---

## 🎯 ÉTAPE 5 - TESTS & DÉPLOIEMENT (3-5 jours)

### Objectif
Valider la solution et mettre en production

### Tests à implémenter
- [ ] Tests unitaires Django (pytest)
- [ ] Tests des endpoints API
- [ ] Tests des modèles et logique métier
- [ ] Tests de l'interface React

### Déploiement
- [ ] Backend: Render.com ou Railway.app
- [ ] Frontend: Vercel
- [ ] PostgreSQL: Supabase ou ElephantSQL
- [ ] Configuration des variables d'env en production

### Tâches
- [ ] Rédiger les tests
- [ ] Configurer CI/CD (GitHub Actions)
- [ ] Déployer le backend
- [ ] Déployer le frontend
- [ ] Tester en production
- [ ] Ajuster les seuils d'alerte

### 📝 Prompts Gemini

**Prompt 16 - Tests unitaires Django**
```
Crée une suite complète de tests pytest pour Django:

1. Tests des modèles:
   - Création d'instances
   - Validations
   - Méthodes personnalisées

2. Tests de la logique métier:
   - Calcul de ratio L/h
   - Détection d'écart (> 20%)
   - Création d'alerte

3. Tests des endpoints API:
   - POST /api/carburant/ avec alerte
   - GET /api/dashboard/
   - Authentification (JWT + PIN)

Structure:
- conftest.py avec fixtures
- Tests séparés par module
- Coverage > 80%

Fournis le code complet avec pytest.ini et requirements-dev.txt
```

**Prompt 17 - Configuration de déploiement**
```
Configure le déploiement complet:

1. Backend Django sur Render.com:
   - Dockerfile optimisé
   - Variables d'env en production
   - Migration automatique DB
   - Healthcheck

2. Frontend React sur Vercel:
   - Build configuration
   - Variables d'env (API_URL)
   - Custom domain (optionnel)

3. PostgreSQL sur Supabase:
   - Création de la DB
   - Backups automatiques
   - Connection string

Fournis tous les fichiers et instructions étape par étape.
```

**Prompt 18 - GitHub Actions CI/CD**
```
Crée un workflow GitHub Actions qui:
1. Exécute les tests à chaque push
2. Bâtit les images Docker
3. Déploie le backend automatiquement sur Render
4. Déploie le frontend automatiquement sur Vercel
5. Notifie les statuts en Slack/Discord (optionnel)

Fichier: .github/workflows/ci-cd.yml
```

### ✍️ Notes & Observations

---

## 🔧 Utilisation rapide avec Gemini

### Option 1: Utiliser l'extension Gemini dans VSCode
1. Installer l'extension Google Gemini dans VSCode
2. Ouvrir ce fichier GEMINI.md
3. Copier-coller chaque prompt dans Gemini
4. Récupérer le code généré
5. Intégrer dans le projet

### Option 2: Gemini en ligne (gemini.google.com)
1. Ouvrir gemini.google.com
2. Copier-coller les prompts
3. Coller le code dans VSCode

### Option 3: Gemini API (pour automatisation)
```bash
# Installer le SDK Python
pip install google-generativeai

# Utiliser dans un script Python
python gemini_helper.py
```

---

## 📊 Checklist Globale

### Préparation
- [ ] GitHub repo créé (carburflow)
- [ ] PostgreSQL local/Docker
- [ ] Structure Django + React setup
- [ ] Variables .env configurées

### Base de données
- [ ] 7 tables créées
- [ ] Migrations Django générées
- [ ] Modèles Django validés
- [ ] Indexes créés

### Backend
- [ ] Endpoints CRUD complétés
- [ ] Authentification JWT + PIN
- [ ] Logique détection écart
- [ ] Job comparaison électricité
- [ ] Tests unitaires > 80%

### Frontend
- [ ] 5 écrans implémentés
- [ ] Formulaires fonctionnels
- [ ] Graphiques dynamiques
- [ ] Responsive design
- [ ] Tests React

### Notifications
- [ ] Bot Telegram intégré
- [ ] Notifications auto déclenchées
- [ ] SMS (optionnel)

### Production
- [ ] Tests en environnement réel
- [ ] Backend déployé
- [ ] Frontend déployé
- [ ] DB en production
- [ ] Seuils d'alerte ajustés

---

## 🎓 Ressources Utiles

### Django
- Django REST Framework: https://www.django-rest-framework.org/
- Django Signals: https://docs.djangoproject.com/en/stable/topics/signals/
- Celery Tasks: https://docs.celeryproject.io/

### React
- React Docs: https://react.dev
- TypeScript + React: https://www.typescriptlang.org/docs/handbook/react.html
- Recharts: https://recharts.org/

### PostgreSQL
- Docker PostgreSQL: https://hub.docker.com/_/postgres
- Supabase: https://supabase.com

### Déploiement
- Render: https://render.com
- Vercel: https://vercel.com
- Railway: https://railway.app

### Notifications
- Telegram Bot: https://python-telegram-bot.readthedocs.io/
- Twilio: https://www.twilio.com/docs/python

---

## 📝 Notes Finales

**Créé le**: [DATE]  
**Dernière mise à jour**: [DATE]  
**Responsable**: Divine  
**Statut global**: ⬜ À faire

### Bloqueurs actuels
_À remplir si blocages rencontrés_

### Prochaines étapes
1. Démarrer par l'Étape 0 avec Gemini
2. Valider chaque étape avant de passer à la suivante
3. Maintenir ce fichier à jour avec la progression
4. Documenter les problèmes rencontrés et solutions

---

**Bonne chance! 🚀**
