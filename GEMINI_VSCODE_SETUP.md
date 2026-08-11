# 🔧 Configuration de Gemini dans VSCode - Guide Complet

## 📌 Table des matières
1. [Installation de l'extension Gemini](#installation)
2. [Configuration de l'API](#configuration)
3. [Utilisation dans le projet](#utilisation)
4. [Workflow recommandé](#workflow)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 Installation

### Option 1: Extension Gemini officielle (Recommandée)

#### Étape 1 - Installer l'extension VSCode
1. Ouvre VSCode
2. Va dans l'onglet **Extensions** (Ctrl+Shift+X / Cmd+Shift+X)
3. Cherche **"Google Gemini"** ou **"Gemini API"**
4. Clique sur **Install** sur l'extension officielle Google

**Extensions recommandées:**
- `Google.gemini` (Officielle Google)
- Ou `Jake-Code.gemini-code-snippets`

#### Étape 2 - Obtenir une clé API Gemini
1. Visite https://ai.google.dev
2. Clique sur **"Get API Key"**
3. Connecte-toi avec ton compte Google
4. Clique sur **"Create API key"**
5. Copie la clé (elle commence par `AIza...`)

#### Étape 3 - Configurer la clé dans VSCode
1. Ouvre la palette de commande (Ctrl+Shift+P / Cmd+Shift+P)
2. Tape: **"Gemini: Set API Key"**
3. Colle ta clé API
4. ✅ C'est configuré!

---

### Option 2: Configuration manuelle avec .env

Si tu préfères une configuration locale:

**Fichier: `.env.local` (à la racine du projet)**
```env
GEMINI_API_KEY=AIza_ta_clé_ici
GEMINI_MODEL=gemini-pro
```

**Fichier: `.vscode/settings.json`**
```json
{
  "gemini.apiKey": "${env:GEMINI_API_KEY}",
  "gemini.model": "gemini-pro",
  "gemini.maxTokens": 4096
}
```

---

## 🔐 Sécurité de la clé API

### ⚠️ Ne jamais commiter la clé API!

**Fichier: `.gitignore`**
```
.env
.env.local
.env*.local
gemini_api_key.txt
```

**Pour le partager en équipe:**
1. Créer un `.env.example` avec des valeurs vides
2. Chaque dev configure sa propre clé
3. Stocker les clés sensibles dans GitHub Secrets (pour CI/CD)

---

## 💡 Utilisation dans le projet

### Méthode 1: Utiliser GEMINI.md directement dans VSCode

**Étape 1 - Ouvrir GEMINI.md**
```bash
# Dans VSCode, ouvre le fichier
Ctrl+O (Cmd+O sur Mac)
# Cherche et ouvre GEMINI.md
```

**Étape 2 - Sélectionner un prompt**
1. Trouve la section de l'étape actuelle
2. Cherche les prompts (marqués avec ### 📝 Prompts Gemini)
3. Sélectionne le prompt entier (triple-clic)

**Étape 3 - Envoyer à Gemini**
- **Raccourci clavier:** Ctrl+Alt+G (ou Cmd+Alt+G sur Mac)
- **Via menu:** Clic-droit → "Send to Gemini"
- **Via palette:** Ctrl+Shift+P → "Gemini: Send Selection"

**Étape 4 - Récupérer la réponse**
- Une fenêtre Gemini s'ouvre
- Le code/texte généré est affiché
- Clique sur **"Copy"** ou **"Insert into Editor"**

---

### Méthode 2: Utiliser le script Python helper

**Installation:**
```bash
# À la racine du projet
pip install google-generativeai

# Exporte ta clé API
export GEMINI_API_KEY="AIza_ta_clé_ici"
```

**Utilisation:**
```bash
# Lance le helper interactif
python gemini_helper.py

# Ou utilise-le dans ton code
from gemini_helper import GeminiHelper

helper = GeminiHelper(project_stage="stage0")
response = helper.generate_code("Créer un modèle Django pour les alertes", "python")
print(response)
```

---

### Méthode 3: Conversation interactive dans VSCode

1. **Ouvre la palette de commandes:** Ctrl+Shift+P
2. **Tape:** "Gemini: New Chat"
3. **Une nouvelle fenêtre s'ouvre** avec un chat interactif
4. **Type tes prompts** et reçois les réponses

**Avantages:**
- Conversation continue avec contexte
- Historique sauvegardé
- Corrections faciles

---

## 🚀 Workflow Recommandé

### Jour 1 - ÉTAPE 0 (Préparation)

```
1. Ouvre GEMINI.md (Ctrl+O)
   ├─ Va à la section "ÉTAPE 0"
   ├─ Sélectionne "Prompt 1 - Structure du projet"
   └─ Envoie à Gemini (Ctrl+Alt+G)

2. Récupère le code généré
   ├─ Crée les fichiers/dossiers suggérés
   ├─ Teste la structure (ls -R)
   └─ Valide que tout est en place

3. Passe à "Prompt 2 - Authentification JWT + PIN"
   └─ Intègre le code dans le projet
```

### Jour 2-3 - ÉTAPE 1 (Base de données)

```
1. "Prompt 3 - Schéma SQL complet"
   ├─ Copie le SQL généré
   ├─ Crée migrations/0001_initial.sql
   └─ Teste avec: psql -d carburflow < migrations/0001_initial.sql

2. "Prompt 4 - Modèles Django"
   ├─ Copie les modèles
   ├─ Crée backend/app/models.py
   └─ Lance: python manage.py makemigrations

3. Revois les modèles avec Gemini (Méthode 3)
   └─ "Revois cette ligne de modèle..." (Ctrl+Alt+G)
```

### Jours 4-7 - ÉTAPE 2 (Backend)

```
1. Prompts 5-8 pour chaque composant (serializers, logique, endpoints)
2. Génère le code avec Gemini
3. Teste les endpoints immédiatement:
   curl -X GET http://localhost:8000/api/dashboard/
4. Si erreur → "Gemini: Debug Error" avec le message
```

---

## 🎯 Bonnes Pratiques d'Utilisation

### ✅ À faire:

1. **Être spécifique dans les prompts:**
   ```
   ✅ BON:
   "Crée un modèle Django Employee avec champs: nom, code_pin, 
    site_associé, score_fiabilité. Inclus validation du PIN 
    (4-6 chiffres)"
   
   ❌ MAUVAIS:
   "Fais un modèle pour les employés"
   ```

2. **Fournir du contexte:**
   ```python
   # Avant d'envoyer un prompt, commente ton code actuel
   # Cela aide Gemini à comprendre ton approche
   ```

3. **Vérifier le code généré:**
   ```bash
   # Ne pas copier-coller aveuglément
   # Teste toujours avant de merger
   pytest tests/test_models.py
   ```

4. **Sauvegarder les conversations:**
   ```bash
   # Utilise le helper pour conserver un historique
   python gemini_helper.py  # puis option 6
   ```

### ❌ À éviter:

1. **Prompts vagues:**
   ```
   ❌ "Fais un API"
   ✅ "Crée un endpoint GET /api/alertes/ qui retourne..."
   ```

2. **Dépendre entièrement de Gemini:**
   - Vérifie toujours le code
   - Teste dans ton environnement
   - Comprends ce que tu implémentes

3. **Partager des données sensibles:**
   ```
   ❌ "J'ai une erreur avec mon token 'ABC123xyz'"
   ✅ "J'ai une erreur avec les tokens JWT"
   ```

---

## 🔄 Intégration avec Git Workflow

### Workflow de développement optimal:

```bash
# 1. Crée une branche pour l'étape
git checkout -b feature/stage0-setup

# 2. Ouvre GEMINI.md et suit les prompts
# 3. Génère du code avec Gemini
# 4. Teste le code généré
# 5. Commit les modifications

git add .
git commit -m "feat(stage0): Initialiser structure Django + React"

# 6. Met à jour GEMINI.md avec le statut
# Dans le fichier, change:
# ✅ Tâche complétée
# [✓] Checkbox marquée

git add GEMINI.md
git commit -m "docs(gemini): Mettre à jour le statut d'étape 0"

# 7. Push et crée une Pull Request
git push origin feature/stage0-setup
```

---

## 📊 Suivre la progression dans GEMINI.md

### Mise à jour du tableau de statut:

**Avant:**
```markdown
| Étape | Statut | % Complété | Dernière MAJ |
|-------|--------|-----------|--------------|
| Étape 0 | ⬜ À faire | 0% | - |
```

**Après (structure créée, pas les endpoints):**
```markdown
| Étape | Statut | % Complété | Dernière MAJ |
|-------|--------|-----------|--------------|
| Étape 0 | 🟨 En cours | 50% | 2024-01-15 |
```

**Après (tout complété):**
```markdown
| Étape | Statut | % Complété | Dernière MAJ |
|-------|--------|-----------|--------------|
| Étape 0 | 🟩 Complété | 100% | 2024-01-15 |
```

---

## 🆘 Troubleshooting

### Problème 1: "API Key is invalid"

**Solution:**
```bash
# Vérifie ta clé
echo $GEMINI_API_KEY

# Reconfigure
Ctrl+Shift+P → "Gemini: Set API Key"

# Ou regénère-la sur https://ai.google.dev
```

### Problème 2: "Extension not found"

**Solution:**
```bash
# Ouvre VSCode de nouveau
# Va dans Extensions → cherche "Gemini"
# Assure-toi d'installer l'officielle Google (plus de 100k téléchargements)
```

### Problème 3: Le code généré ne s'insère pas

**Solution alternative:**
1. Copie manuellement la réponse de Gemini
2. Crée un nouveau fichier
3. Colle le code
4. Formate avec Ctrl+Shift+F

### Problème 4: Timeout ou réponse lente

**Solution:**
```bash
# Réduis la taille du prompt
# Divise un grand prompt en 2-3 petits prompts

# Ou utilise un modèle plus rapide
# Dans VSCode settings:
"gemini.model": "gemini-1.5-flash"  # Plus rapide, moins puissant
```

### Problème 5: La réponse de Gemini n'est pas assez détaillée

**Solution:**
```
Ajoute à ton prompt:
"Fournis aussi:
- Explications ligne par ligne
- Points clés à retenir
- Liens vers la documentation
- Alternatives si applicable"
```

---

## 🎓 Ressources Utiles

### Documentation Gemini
- [Gemini API Docs](https://ai.google.dev/docs)
- [Gemini Tutorials](https://ai.google.dev/tutorials)
- [Prompt Engineering Guide](https://ai.google.dev/docs/prompt_engineering)

### Prompting Tips
- Sois clair et précis
- Fournisse du contexte
- Demande des explications
- Utilise des formats (markdown, JSON, etc.)
- Itère si la première réponse n'est pas parfaite

### Extensions VSCode utiles
- `Python` (Microsoft)
- `Pylance` (Microsoft)
- `ES7+ React/Redux/React-Native snippets`
- `Prettier` (formateur de code)
- `Thunder Client` (tester les APIs)

---

## 📋 Checklist de Configuration

```
☐ Extension Gemini installée dans VSCode
☐ Clé API Gemini générée (https://ai.google.dev)
☐ Clé API configurée dans VSCode
☐ .gitignore contient .env
☐ GEMINI.md ouvert et accessible
☐ gemini_helper.py dans le projet
☐ google-generativeai installé (pip install google-generativeai)
☐ Première utilisation testée (Gemini: New Chat)
☐ Ce guide lu entièrement
☐ Prêt à démarrer ÉTAPE 0 ! 🚀
```

---

## 🎉 C'est prêt!

Tu es maintenant configuré pour utiliser Gemini dans ton projet CAMTEL!

**Prochaines étapes:**
1. Lis attentivement GEMINI.md
2. Ouvre VSCode et la palette de commandes
3. Tape "Gemini: New Chat" pour tester
4. Envoie un premier prompt pour valider la configuration
5. Commence par l'ÉTAPE 0!

**Questions?**
- Consulte ce fichier (GEMINI_VSCODE_SETUP.md)
- Ou demande directement à Gemini: "Comment fais-je... dans VSCode?"

**Bonne chance! 🚀**

---

**Créé pour:** Projet CAMTEL - Plateforme de Gestion de Carburant  
**Version:** 1.0  
**Dernière mise à jour:** 2024
