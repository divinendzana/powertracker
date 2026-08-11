Documentation technique
1. Présentation du projet
PowerTracker est une application de suivi des coupures électriques, des sessions d'utilisation du groupe électrogène, des pleins de carburant et de la consommation électrique, pour deux sites : une maison et un restaurant. L'objectif est de détecter automatiquement les anomalies (surconsommation de carburant, écarts inhabituels de consommation électrique) et d'alerter l'administrateur en temps réel.
2. Architecture technique
Composant	Technologie
Backend / API	Django + Django REST Framework
Base de données	PostgreSQL
Frontend	React
Authentification	JWT (admin) / PIN (employés)
Tâches planifiées	Celery + cron (ou tâche périodique simple)
Notifications	Bot Telegram ou API SMS (Twilio)
Déploiement backend	Render / Railway
Déploiement frontend	Vercel

3. Modèle de données
Le schéma relationnel repose sur sept tables principales, reliées entre elles par les identifiants de site et d'employé :
•	sites : identifie chaque emplacement (maison, restaurant)
•	employes : informations d'authentification (PIN) et rattachement à un site, avec un score de fiabilité calculé
•	coupures : historique des coupures électriques déclarées (début, fin, déclarant)
•	groupe_sessions : sessions d'utilisation du groupe électrogène, avec durée calculée automatiquement
•	pleins_carburant : historique des achats de carburant (litres, prix, date, employé)
•	consommation_electricite : relevés mensuels de consommation (kWh ou montant facturé)
•	alertes : anomalies détectées automatiquement par le système, avec statut de résolution
4. Endpoints API (Django REST Framework)
Méthode	Route	Description
POST	/coupures/	Déclarer le début ou la fin d'une coupure
POST	/groupe/demarrer	Démarrer une session groupe électrogène
POST	/groupe/arreter	Arrêter une session groupe électrogène
POST	/carburant/	Enregistrer un plein de carburant
GET	/dashboard/	Récupérer les statistiques consolidées

5. Logique métier clé
Détection d'écart sur le carburant
À chaque nouveau plein de carburant enregistré, un service calcule le ratio litres/heure attendu à partir de la moyenne historique du site, puis le compare au ratio réellement déclaré. Si l'écart dépasse un seuil défini, une entrée est créée dans la table `alertes`.
Détection d'écart sur la consommation électrique
Un job planifié (Celery + cron, ou tâche périodique équivalente) compare chaque mois la consommation électrique du site au mois en cours par rapport aux mois précédents. Toute incohérence significative génère automatiquement une alerte.
6. Rôles et authentification
•	Administrateur : authentification par JWT, accès complet au tableau de bord, à l'historique et à la gestion des alertes
•	Employé : authentification simplifiée par code PIN, accès limité aux écrans de déclaration (coupure, groupe électrogène, plein de carburant)
7. Notifications
Dès qu'une alerte est créée côté backend, une notification est envoyée automatiquement via un bot Telegram ou une API SMS (Twilio), afin que l'administrateur soit informé en temps réel sans avoir à consulter le tableau de bord.
8. Déploiement
•	Backend Django déployé sur Render ou Railway
•	Frontend React déployé sur Vercel
•	Base de données PostgreSQL managée (fournie par la plateforme d'hébergement choisie)
•	Après mise en production, les seuils d'alerte sont ajustés progressivement selon les faux positifs observés en usage réel
9. Suivi du projet
Ce document sert de référence pour le suivi de l'avancement du projet PowerTracker. Chaque étape peut être cochée au fur et à mesure de son achèvement, et la documentation technique peut être enrichie à mesure que l'implémentation avance (schémas détaillés, captures d'écran, exemples de requêtes API, etc.).
