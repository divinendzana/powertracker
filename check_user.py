#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from tracker.models import Site, Employe, Coupure, PleineCarburant, Alerte
from django.contrib.auth.models import User

print("=" * 50)
print("🚀 Initialisation des données de test PowerTracker")
print("=" * 50)

# 1. Créer les sites
print("\n📍 Création des sites...")
sites_data = [
    {
        'nom': 'Siège Douala',
        'adresse': 'Boulevard de la Liberté, Douala',
        'type_carburant': 'essence',
        'type_groupe': 'Cummins 500KVA',
        'puissance_kva': 500.0,
        'actif': True
    },
    {
        'nom': 'Restaurant Yaoundé',
        'adresse': 'Avenue Kennedy, Yaoundé',
        'type_carburant': 'gazoil',
        'type_groupe': 'Perkins 250KVA',
        'puissance_kva': 250.0,
        'actif': True
    },
    {
        'nom': 'Antenne Bamenda',
        'adresse': 'Rue de la République, Bamenda',
        'type_carburant': 'gazoil',
        'type_groupe': 'Perkins 150KVA',
        'puissance_kva': 150.0,
        'actif': True
    },
    {
        'nom': 'Bâtiment Annexe Kribi',
        'adresse': 'Route Kribi-Elima, Kribi',
        'type_carburant': 'essence',
        'type_groupe': 'Cummins 100KVA',
        'puissance_kva': 100.0,
        'actif': False
    },
]

sites = {}
for site_data in sites_data:
    site, created = Site.objects.get_or_create(
        nom=site_data['nom'],
        defaults=site_data
    )
    sites[site_data['nom']] = site
    if created:
        print(f"  ✓ Site créé: {site.nom}")
    else:
        print(f"  • Site existant: {site.nom}")

print(f"\n✓ Sites créés: {Site.objects.count()}")

# 2. Créer les employés
print("\n👤 Création des employés...")

employes_data = [
    {
        'email': 'admindivine@camtel.cm',
        'nom': 'Divine',
        'prenom': 'Admin',
        'role': 'administratrice',
        'telephone': '237699000000',
        'actif': True
    },
    {
        'email': 'jean.mbarga@camtel.cm',
        'nom': 'Mbarga',
        'prenom': 'Jean',
        'role': 'employe',
        'telephone': '237677000000',
        'site': sites['Siège Douala'],
        'actif': True
    },
    {
        'email': 'marie.douala@camtel.cm',
        'nom': 'Douala',
        'prenom': 'Marie',
        'role': 'employe',
        'telephone': '237688000000',
        'site': sites['Restaurant Yaoundé'],
        'actif': True
    },
    {
        'email': 'paul.bamenda@camtel.cm',
        'nom': 'Bamenda',
        'prenom': 'Paul',
        'role': 'employe',
        'telephone': '237699111111',
        'site': sites['Antenne Bamenda'],
        'actif': True
    },
    {
        'email': 'sophie.kribi@camtel.cm',
        'nom': 'Kribi',
        'prenom': 'Sophie',
        'role': 'employe',
        'telephone': '237677222222',
        'site': sites['Bâtiment Annexe Kribi'],
        'actif': True
    },
]

for emp_data in employes_data:
    email = emp_data.pop('email')
    role = emp_data.pop('role')
    site = emp_data.pop('site', None)
    
    # Créer User Django
    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email}
    )
    if created:
        user.set_password('divi1234')
        user.save()
    
    # Créer Employe
    employe, created = Employe.objects.get_or_create(
        email=email,
        defaults={**emp_data, 'role': role, 'site': site}
    )
    if created:
        print(f"  ✓ Employé créé: {employe.nom} {employe.prenom}")
    else:
        print(f"  • Employé existant: {employe.nom} {employe.prenom}")

print(f"\n✓ Employés créés: {Employe.objects.count()}")

# 3. Créer des coupures de test
print("\n⚡ Création des coupures...")

from datetime import datetime, timedelta
now = datetime.now()

coupures_data = [
    {
        'site': sites['Restaurant Yaoundé'],
        'date_debut': now - timedelta(hours=3),
        'date_fin': now - timedelta(hours=2),
        'statut': 'fermee',
        'employe': Employe.objects.get(email='marie.douala@camtel.cm'),
        'cause_descriptif': 'Problème réseau'
    },
    {
        'site': sites['Siège Douala'],
        'date_debut': now - timedelta(hours=1),
        'date_fin': None,
        'statut': 'ouverte',
        'employe': Employe.objects.get(email='jean.mbarga@camtel.cm'),
        'cause_descriptif': None
    },
    {
        'site': sites['Antenne Bamenda'],
        'date_debut': now - timedelta(days=1, hours=2),
        'date_fin': now - timedelta(days=1, hours=1),
        'statut': 'fermee',
        'employe': Employe.objects.get(email='paul.bamenda@camtel.cm'),
        'cause_descriptif': 'Panne technique'
    },
    {
        'site': sites['Bâtiment Annexe Kribi'],
        'date_debut': now - timedelta(days=2),
        'date_fin': now - timedelta(days=2, hours=1),
        'statut': 'fermee',
        'employe': Employe.objects.get(email='sophie.kribi@camtel.cm'),
        'cause_descriptif': 'Maintenance préventive'
    },
]

for coupure_data in coupures_data:
    site = coupure_data.pop('site')
    statut = coupure_data.pop('statut')
    employe = coupure_data.pop('employe')
    cause = coupure_data.pop('cause_descriptif')
    
    coupure, created = Coupure.objects.get_or_create(
        site=site,
        date_debut=coupure_data['date_debut'],
        defaults={
            **coupure_data,
            'statut': statut,
            'employe_id_declaration': employe
        }
    )
    if created:
        print(f"  ✓ Coupure créée: {site.nom} - {coupure.date_debut.strftime('%d/%m %H:%M')}")

print(f"\n✓ Coupures créées: {Coupure.objects.count()}")

# 4. Créer des pleins de carburant
print("\n⛽ Création des pleins...")

pleins_data = [
    {
        'site': sites['Siège Douala'],
        'date_plein': now - timedelta(days=1),
        'quantite_litres': 500.0,
        'prix_unitaire_fcfa': 500.0,
        'employe': Employe.objects.get(email='jean.mbarga@camtel.cm'),
    },
    {
        'site': sites['Restaurant Yaoundé'],
        'date_plein': now - timedelta(hours=5),
        'quantite_litres': 200.0,
        'prix_unitaire_fcfa': 500.0,
        'employe': Employe.objects.get(email='marie.douala@camtel.cm'),
    },
    {
        'site': sites['Antenne Bamenda'],
        'date_plein': now - timedelta(days=2),
        'quantite_litres': 150.0,
        'prix_unitaire_fcfa': 500.0,
        'employe': Employe.objects.get(email='paul.bamenda@camtel.cm'),
    },
    {
        'site': sites['Bâtiment Annexe Kribi'],
        'date_plein': now - timedelta(days=3),
        'quantite_litres': 100.0,
        'prix_unitaire_fcfa': 500.0,
        'employe': Employe.objects.get(email='sophie.kribi@camtel.cm'),
    },
]

for plein_data in pleins_data:
    site = plein_data.pop('site')
    employe = plein_data.pop('employe')
    
    plein, created = PleineCarburant.objects.get_or_create(
        site=site,
        date_plein=plein_data['date_plein'],
        defaults={
            **plein_data,
            'employe_id_declaration': employe
        }
    )
    if created:
        print(f"  ✓ Plein créé: {site.nom} - {plein.quantite_litres}L")

print(f"\n✓ Pleins créés: {PleineCarburant.objects.count()}")

# 5. Créer des alertes
print("\n⚠️ Création des alertes...")

alertes_data = [
    {
        'site': sites['Siège Douala'],
        'type_alerte': 'carburant_anomalie',
        'severite': 'bas',
        'motif_technique': 'Stock de carburant faible sur Siège Douala',
        'valeur_detectee': 150.0,
        'valeur_seuil': 200.0,
        'statut': 'resolu',
        'employe_lien': Employe.objects.get(email='jean.mbarga@camtel.cm'),
        'timestamp_creation': now - timedelta(hours=2),
    },
    {
        'site': sites['Antenne Bamenda'],
        'type_alerte': 'electricite_anomalie',
        'severite': 'moyen',
        'motif_technique': 'Coupure de plus de 2h sur Antenne Bamenda',
        'valeur_detectee': 3.5,
        'valeur_seuil': 2.0,
        'statut': 'resolu',
        'employe_lien': Employe.objects.get(email='paul.bamenda@camtel.cm'),
        'timestamp_creation': now - timedelta(days=1),
    },
    {
        'site': sites['Restaurant Yaoundé'],
        'type_alerte': 'carburant_anomalie',
        'severite': 'haut',
        'motif_technique': 'Stock de carburant critique sur Restaurant Yaoundé',
        'valeur_detectee': 50.0,
        'valeur_seuil': 100.0,
        'statut': 'actif',
        'employe_lien': Employe.objects.get(email='marie.douala@camtel.cm'),
        'timestamp_creation': now - timedelta(hours=1),
    },
]

for alerte_data in alertes_data:
    type_alerte = alerte_data.pop('type_alerte')
    severite = alerte_data.pop('severite')
    statut = alerte_data.pop('statut')
    employe_lien = alerte_data.pop('employe_lien')
    timestamp = alerte_data.pop('timestamp_creation')
    site = alerte_data.pop('site')
    
    alerte, created = Alerte.objects.get_or_create(
        site=site,
        type_alerte=type_alerte,
        timestamp_creation=timestamp,
        defaults={
            **alerte_data,
            'severite': severite,
            'statut': statut,
            'employe_id_lien': employe_lien
        }
    )
    if created:
        print(f"  ✓ Alerte créée: {employe_lien.nom} {employe_lien.prenom} - {type_alerte}")

print(f"\n✓ Alertes créées: {Alerte.objects.count()}")

print("\n" + "=" * 50)
print("✅ Initialisation terminée!")
print("=" * 50)

print("\n📊 Résumé:")
print(f"  - Sites créés: {Site.objects.count()}")
print(f"  - Employés créés: {Employe.objects.count()}")
print(f"  - Coupures créées: {Coupure.objects.count()}")
print(f"  - Pleins créés: {PleineCarburant.objects.count()}")
print(f"  - Alertes créées: {Alerte.objects.count()}")

print("\n📍 URL de l'application: http://localhost:3001")
print("📧 Email: admindivine@camtel.cm")
print("🔑 Mot de passe: divi1234")