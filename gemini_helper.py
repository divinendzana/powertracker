#!/usr/bin/env python3
"""
🤖 Gemini Helper pour le projet CAMTEL
Facilite l'utilisation de Gemini pour générer du code étape par étape
"""

import os
import json
from typing import Optional
import google.generativeai as genai

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
MODEL = "gemini-pro"

# Initialiser Gemini
genai.configure(api_key=GEMINI_API_KEY)


class GeminiHelper:
    """Helper pour interagir avec Gemini pour le projet CAMTEL"""
    
    def __init__(self, project_stage: str = "stage0"):
        """
        Initialise le helper pour une étape spécifique du projet
        
        Args:
            project_stage: 'stage0', 'stage1', 'stage2', 'stage3', 'stage4', 'stage5'
        """
        self.stage = project_stage
        self.model = genai.GenerativeModel(MODEL)
        self.conversation_history = []
    
    def ask(self, prompt: str) -> str:
        """
        Envoie un prompt à Gemini et reçoit une réponse
        
        Args:
            prompt: Le prompt à envoyer
            
        Returns:
            La réponse de Gemini
        """
        print(f"\n📤 Envoi du prompt à Gemini...")
        
        # Ajouter le contexte du projet
        contexte = self._get_stage_context()
        prompt_complet = f"{contexte}\n\n{prompt}"
        
        # Générer la réponse
        response = self.model.generate_content(prompt_complet)
        result = response.text
        
        # Sauvegarder dans l'historique
        self.conversation_history.append({
            "prompt": prompt,
            "response": result
        })
        
        print(f"✅ Réponse reçue de Gemini\n")
        return result
    
    def _get_stage_context(self) -> str:
        """Retourne le contexte approprié pour l'étape actuelle"""
        contexts = {
            "stage0": """
Tu es un assistant expert en développement Django + React.
Je travaille sur l'ÉTAPE 0 - PRÉPARATION du projet CAMTEL.
Mon objectif: Mettre en place l'infrastructure de développement.
Stack: Django (backend), React (frontend), PostgreSQL (DB)
            """,
            "stage1": """
Tu es un expert en conception de bases de données PostgreSQL.
Je travaille sur l'ÉTAPE 1 - MODÉLISATION DE LA BASE DE DONNÉES.
Mon objectif: Concevoir et implémenter le schéma SQL avec 7 tables.
Contexte: Plateforme de gestion de carburant pour CAMTEL.
            """,
            "stage2": """
Tu es un expert Django et Django REST Framework.
Je travaille sur l'ÉTAPE 2 - BACKEND DJANGO.
Mon objectif: Développer l'API REST complète avec logique métier.
Endpoints clés: Coupures, Groupe électrogène, Carburant, Dashboard, Alertes
            """,
            "stage3": """
Tu es un expert React et TypeScript.
Je travaille sur l'ÉTAPE 3 - FRONTEND REACT.
Mon objectif: Développer l'interface utilisateur interactive.
Écrans: Login, Coupures, Groupe, Dashboard, Historique
            """,
            "stage4": """
Tu es un expert en intégrations et notifications.
Je travaille sur l'ÉTAPE 4 - NOTIFICATIONS.
Mon objectif: Implémenter les alertes en temps réel.
Canaux: Telegram Bot, SMS (optionnel)
            """,
            "stage5": """
Tu es un expert en tests et déploiement.
Je travaille sur l'ÉTAPE 5 - TESTS & DÉPLOIEMENT.
Mon objectif: Valider et mettre en production.
Déploiement: Render (backend), Vercel (frontend), Supabase (DB)
            """
        }
        return contexts.get(self.stage, "")
    
    def generate_code(self, feature: str, language: str = "python") -> str:
        """
        Génère du code pour une fonctionnalité spécifique
        
        Args:
            feature: Description de la fonctionnalité
            language: 'python', 'javascript', 'typescript', 'sql'
            
        Returns:
            Le code généré
        """
        prompt = f"""
Génère du code {language} pour: {feature}

Requirements:
1. Code prêt à la production
2. Avec commentaires explicatifs
3. Gestion d'erreurs incluse
4. Respects des bonnes pratiques

Formate la réponse comme:
```{language}
[code ici]
```

Avant le code, explique brièvement ce qu'il fait.
        """
        return self.ask(prompt)
    
    def debug_error(self, error: str, code_snippet: Optional[str] = None) -> str:
        """
        Aide à déboguer une erreur
        
        Args:
            error: Le message d'erreur
            code_snippet: Le code qui cause l'erreur (optionnel)
            
        Returns:
            L'explication et la solution
        """
        prompt = f"""
J'ai une erreur dans mon code:

Erreur: {error}
"""
        if code_snippet:
            prompt += f"""

Code concerné:
```
{code_snippet}
```
"""
        prompt += """

Aide-moi à:
1. Comprendre la cause de l'erreur
2. Proposer une solution
3. Fournir le code corrigé
"""
        return self.ask(prompt)
    
    def review_code(self, code: str, language: str = "python") -> str:
        """
        Revoit du code et suggère des améliorations
        
        Args:
            code: Le code à réviser
            language: Le langage du code
            
        Returns:
            Les commentaires et suggestions
        """
        prompt = f"""
Revois ce code {language}:

```{language}
{code}
```

Pour chaque suggestion:
1. Explique le problème
2. Propose une amélioration
3. Donne l'alternative

Focus sur:
- Performance
- Lisibilité
- Sécurité
- Bonnes pratiques
        """
        return self.ask(prompt)
    
    def save_conversation(self, filename: str = None) -> str:
        """
        Sauvegarde l'historique de conversation
        
        Args:
            filename: Nom du fichier (par défaut: conversation_stage_[timestamp].json)
            
        Returns:
            Chemin du fichier sauvegardé
        """
        if not filename:
            import time
            timestamp = int(time.time())
            filename = f"conversation_{self.stage}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Conversation sauvegardée dans {filename}")
        return filename


# Prompts pré-définis pour chaque étape
STAGE_PROMPTS = {
    "stage0_project_setup": """
Aide-moi à configurer le projet Django + React pour CAMTEL.
Génère:
1. Structure de dossiers complète (backend/, frontend/)
2. Fichiers de configuration (.env, .gitignore, docker-compose.yml)
3. requirements.txt (Python)
4. package.json (Node.js)
5. Dockerfile (pour PostgreSQL)

Inclus des explications pour chaque fichier.
    """,
    
    "stage1_database_schema": """
Génère le schéma PostgreSQL complet pour:
- sites (maison, restaurant)
- employees (avec PIN)
- coupures (avec durée)
- groupe_sessions
- pleins_carburant
- consommation_electricite
- alertes

Inclus:
- Types de données optimisés
- Primary keys et foreign keys
- Indexes pour les requêtes fréquentes
- Contraintes et validations
- Commentaires explicatifs
    """,
    
    "stage2_django_models": """
Convertis le schéma SQL en modèles Django complets.
Pour chaque modèle:
1. Tous les champs avec types appropriés
2. Validateurs personnalisés
3. Méthodes __str__
4. Meta options
5. Managers personnalisés si utile

Génère aussi les serializers Django REST Framework.
    """,
    
    "stage2_business_logic": """
Implémente la logique métier clé:

1. Détection d'écart carburant:
   - Signal après création d'un PleinCarburant
   - Calculer ratio L/h moyen historique
   - Créer Alerte si écart > 20%

2. Job de comparaison électricité:
   - Tâche planifiée (chaque mois)
   - Comparer conso mois courant vs 3 mois précédents
   - Créer Alerte si anomalie (+50%)

Fournisse le code Django complet avec signals et gestion d'erreurs.
    """,
    
    "stage3_react_dashboard": """
Crée un composant Dashboard React qui affiche:
1. Nombre total de coupures (mois courant)
2. Litres de carburant consommés
3. Coût total carburant
4. Nombre d'alertes actives
5. Graphique carburant par site (Recharts)
6. Tableau des alertes avec tri/filtrage

Utilise:
- React Hooks (useState, useEffect)
- TypeScript
- Axios pour l'API
- Tailwind CSS
- Recharts pour les graphiques
    """,
    
    "stage4_telegram_bot": """
Intègre un bot Telegram à Django qui:
1. Envoie une notification quand une Alerte est créée
2. Format: "🚨 Alerte [Type] - [Message] pour [Site]"
3. Gère les erreurs de connexion
4. Stocke l'historique des notifications

Génère:
- Modèle AlerteNotification
- Service TelegramNotifier
- Configuration et variables d'env
- Instructions pour créer le bot
- Django signal pour déclencher automatiquement
    """,
}


def main():
    """Exemple d'utilisation du helper"""
    
    print("="*60)
    print("🤖 Gemini Helper - Projet CAMTEL")
    print("="*60)
    
    # Vérifier la clé API
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  ERREUR: Définis GEMINI_API_KEY en variable d'environnement")
        print("Export: export GEMINI_API_KEY='ta_clé_ici'")
        return
    
    # Menu interactif
    print("\nChoisir l'étape du projet:")
    stages = {
        "0": ("stage0", "Étape 0 - Préparation"),
        "1": ("stage1", "Étape 1 - Modélisation DB"),
        "2": ("stage2", "Étape 2 - Backend Django"),
        "3": ("stage3", "Étape 3 - Frontend React"),
        "4": ("stage4", "Étape 4 - Notifications"),
        "5": ("stage5", "Étape 5 - Tests & Deploy"),
    }
    
    for key, (stage_id, desc) in stages.items():
        print(f"{key}. {desc}")
    
    choice = input("\nChoix (0-5): ").strip()
    if choice not in stages:
        print("Choix invalide")
        return
    
    stage_id, stage_desc = stages[choice]
    print(f"\n✅ Sélectionné: {stage_desc}")
    
    # Initialiser le helper
    helper = GeminiHelper(stage_id)
    
    # Menu des actions
    print("\nActions disponibles:")
    print("1. Utiliser un prompt pré-défini")
    print("2. Écrire un prompt personnalisé")
    print("3. Générer du code")
    print("4. Réviser du code")
    print("5. Déboguer une erreur")
    print("6. Sauvegarder la conversation")
    
    action = input("\nAction (1-6): ").strip()
    
    if action == "1":
        # Prompts pré-définis
        print("\nPrompts disponibles:")
        available_prompts = {k: v for k in STAGE_PROMPTS.keys() if stage_id in k}
        for i, (key, prompt) in enumerate(available_prompts.items(), 1):
            print(f"{i}. {key}")
        
        if available_prompts:
            prompt_choice = int(input("Choix: ")) - 1
            prompt_key = list(available_prompts.keys())[prompt_choice]
            prompt_text = STAGE_PROMPTS[prompt_key]
            
            response = helper.ask(prompt_text)
            print("\n" + response)
    
    elif action == "2":
        # Prompt personnalisé
        print("\nÉcris ton prompt (termine par une ligne vide):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        prompt_text = "\n".join(lines)
        response = helper.ask(prompt_text)
        print("\n" + response)
    
    elif action == "3":
        # Générer du code
        feature = input("Description de la fonctionnalité: ")
        language = input("Langage (python/javascript/typescript/sql): ").strip()
        response = helper.generate_code(feature, language)
        print("\n" + response)
    
    elif action == "4":
        # Réviser du code
        print("Colle ton code (termine par une ligne vide):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        code = "\n".join(lines)
        response = helper.review_code(code)
        print("\n" + response)
    
    elif action == "5":
        # Déboguer
        error = input("Message d'erreur: ")
        code = input("Code concerné (optionnel, vide pour ignorer): ").strip()
        response = helper.debug_error(error, code if code else None)
        print("\n" + response)
    
    elif action == "6":
        # Sauvegarder
        filename = input("Nom du fichier (vide = auto): ").strip()
        saved = helper.save_conversation(filename if filename else None)
        print(f"\n✅ Sauvegardé: {saved}")


if __name__ == "__main__":
    main()
