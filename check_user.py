#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from tracker.models import Employe, Site

try:
    # Créer le site si nécessaire
    site, created = Site.objects.get_or_create(
        nom='Restaurant Yaoundé',
        defaults={
            'adresse': 'Avenue Kennedy',
            'type_carburant': 'gazoil',
            'actif': True
        }
    )
    if created:
        print(f'Site créé: {site.nom}')
    
    # Créer ou mettre à jour l'utilisateur
    user, created = Employe.objects.get_or_create(
        email='admindivine@camtel.cm',
        defaults={
            'nom': 'Divine',
            'prenom': 'Admin',
            'role': Employe.Role.ADMINISTRATRICE,
            'telephone': '237XXXXXXXX',
            'actif': True
        }
    )
    
    # Mettre à jour le PIN (avec hash)
    user.set_pin('divi1234')
    user.save()
    
    if created:
        print(f'Utilisateur créé avec succès!')
    else:
        print(f'Utilisateur mis à jour avec succès!')
    
    print(f'Email: {user.email}')
    print(f'Nom: {user.nom} {user.prenom}')
    print(f'PIN: divi1234')
    print(f'Role: {user.role}')
    print(f'Site: {user.site.name if user.site else None}')
    print(f'Status: Actif' if user.actif else 'Status: Inactif')
    
    print(f'\\n✅ Compte administrateur prêt!')
    print(f'\\n📍 URL: http://localhost:3001')
    print(f'\\n📧 Email: admindivine@camtel.cm')
    print(f'🔑 Mot de passe: divi1234')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()