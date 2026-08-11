# ⚡ Quick Start - CAMTEL + Gemini en 5 minutes

**Prêt à lancer le projet? Voici le chemin le plus court.**

---

## 🚀 Étape 1: Configuration (2 min)

### 1.1 Obtenir une clé Gemini
```bash
# Visite: https://ai.google.dev
# Clique: "Get API Key"
# Connecte toi avec Google
# Copie la clé (commence par AIza...)
```

### 1.2 Configurer VSCode
1. Ouvre VSCode
2. **Ctrl+Shift+X** (Extensions)
3. Cherche: `Google Gemini` ou `google.gemini`
4. Clique: **Install**
5. **Ctrl+Shift+P** → Tape: `Gemini: Set API Key`
6. Colle ta clé

✅ **C'est prêt!**

---

## 📂 Étape 2: Copier les fichiers (1 min)

Copie ces fichiers dans ton projet:
```
ton-projet/
├── GEMINI.md ..................... (La roadmap interactive)
├── GEMINI_VSCODE_SETUP.md ........ (Guide détaillé VSCode)
├── .env.example .................. (Variables de configuration)
└── gemini_helper.py .............. (Script Python helper)
```

**Comment copier:**
```bash
# Si tu as cloné notre repo
cp GEMINI.md GEMINI_VSCODE_SETUP.md .env.example gemini_helper.py ~/mon-projet/

# Renomme le .env.example
cd ~/mon-projet/
cp .env.example .env
```

---

## 🎯 Étape 3: Premier test (1 min)

### Test 1 - Chat Gemini dans VSCode

1. Ouvre VSCode
2. **Ctrl+Shift+P** → Tape: `Gemini: New Chat`
3. Dans le chat, tape:
```
Bonjour Gemini! Je travaille sur une plateforme Django + React 
pour gérer les consommations de carburant. 
Comment dois-je structurer mon projet?
```
4. Vérifie que tu reçois une réponse ✅

### Test 2 - Gemini Helper (Python)

```bash
# Installation
pip install google-generativeai

# Export de la clé (Linux/Mac)
export GEMINI_API_KEY="AIza_ta_clé_ici"

# Sur Windows PowerShell:
# $env:GEMINI_API_KEY="AIza_ta_clé_ici"

# Lance le helper
python gemini_helper.py

# Sélectionne: 0 (Stage 0 - Préparation)
# Sélectionne: 1 (Prompt pré-défini)
# Sélectionne: 1 (Project Setup)
```

✅ **Tu as reçu une réponse?** Continue!

---

## 💻 Étape 4: Créer la structure du projet (1 min)

**Ouvre GEMINI.md** dans VSCode:
1. **Ctrl+O** → Cherche `GEMINI.md`
2. Va à la section **ÉTAPE 0 - PRÉPARATION**
3. Cherche **Prompt 1 - Structure du projet**
4. Sélectionne tout le prompt (triple-clic)
5. **Ctrl+Alt+G** (ou clic-droit → Send to Gemini)
6. Copie la réponse
7. Crée les dossiers/fichiers suggérés

```bash
# Par exemple, crée la structure de base
mkdir -p carburflow/{backend,frontend,docs}
cd carburflow
git init
```

---

## ⚡ Étape 5: Workflow - Comment utiliser Gemini chaque jour (Répété)

### Workflow typique (pour chaque étape):

```
┌─────────────────────────────────────────┐
│ 1. Ouvre GEMINI.md                       │
│    Ctrl+O → GEMINI.md                    │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 2. Va à l'étape actuelle                 │
│    (ex: ÉTAPE 2 - Backend Django)        │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 3. Sélectionne un prompt                 │
│    (ex: Prompt 5 - Serializers Django)   │
│    Triple-clic sur le prompt             │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 4. Envoie à Gemini                       │
│    Ctrl+Alt+G                            │
│    Ou: Clic-droit → Send to Gemini       │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 5. Copie la réponse                      │
│    Ctrl+C dans la fenêtre Gemini         │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 6. Colle dans ton fichier                │
│    Ouvre le fichier cible (ex: models.py)│
│    Ctrl+V pour coller                    │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 7. Teste le code                         │
│    python manage.py test                 │
│    pytest tests/                         │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 8. Si erreur: demande à Gemini!          │
│    Ctrl+Shift+P → Gemini: New Chat       │
│    Colle le message d'erreur             │
└────────────┬──────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 9. Mise à jour GEMINI.md                 │
│    Marque la tâche comme complétée [✓]   │
│    Ajoute la date                        │
└────────────┬──────────────────────────────┘
             │
             ▼
         ✅ RÉPÈTE
```

---

## 🎓 Exemples d'utilisation concrets

### Exemple 1: Créer un modèle Django

**Dans GEMINI.md, Étape 1, Prompt 4:**
```
Convertis ce schéma SQL en modèles Django (models.py):

[SCHÉMA SQL]

Génère:
1. Tous les modèles Django...
```

**Résultat:** Code Django prêt à copier-coller

---

### Exemple 2: Déboguer une erreur

**Dans VSCode:**
1. Tu reçois une erreur Python
2. **Ctrl+Shift+P** → `Gemini: New Chat`
3. Colle l'erreur:
```
NameError: name 'Employee' is not defined
  File "backend/app/views.py", line 45
```
4. Gemini te propose une solution
5. Applique le fix et relance ✅

---

### Exemple 3: Revoir du code

**Dans VSCode:**
1. Sélectionne une fonction que tu veux revoir
2. **Ctrl+Shift+P** → `Gemini: New Chat`
3. Tape:
```
Revois ce code et suggère des améliorations:

[COLLE TON CODE]
```
4. Reçois les suggestions 💡
5. Applique les améliorations

---

## 📊 Checklist Daily

Chaque matin, avant de coder:

```
☐ Ouvre GEMINI.md
☐ Vérifie l'étape actuelle
☐ Lis le prompt du jour
☐ Lance Gemini (Ctrl+Alt+G ou Chat)
☐ Génère le code
☐ Tests le code
☐ Mets à jour GEMINI.md (% et date)
☐ Commit à Git
☐ C'est bon! Continue vers le prochain prompt 🚀
```

---

## 🔥 Astuces Pro

### Astuce 1: Prompts en multi-lignes
Quand un prompt est long:
1. **Ctrl+Shift+P** → `Gemini: New Chat`
2. Colle le prompt en entier
3. Appuie sur **Enter** pour envoyer

### Astuce 2: Sauvegarder les conversations
```bash
# Le helper sauvegarde automatiquement
python gemini_helper.py  # Choix: 6 (Save)

# Les fichiers JSON sont créés:
# conversation_stage0_1705324800.json
```

### Astuce 3: Combiner plusieurs réponses
Si Gemini répond en deux parties:
```
1️⃣ Première réponse (models.py)
2️⃣ Deuxième réponse (serializers.py)

Tu peux créer 2 fichiers séparés et les importer
```

### Astuce 4: Itérer sur une réponse
Si la première réponse n'est pas parfaite:
```
Gemini: "Voici le code..."
Toi: "Améliore-le en ajoutant des validations"
Gemini: "Voici amélioré..."
Toi: "Ajoute la documentation"
... et ainsi de suite
```

---

## ❌ Erreurs courantes et fixes

### ❌ "API Key is invalid"
```bash
# Regénère la clé sur https://ai.google.dev
# Reconfigure dans VSCode (Ctrl+Shift+P → Gemini: Set API Key)
```

### ❌ "Extension not found"
```bash
# Réinstalle l'extension Google Gemini
# Redémarre VSCode
# Ctrl+Shift+X → cherche "gemini" → Install
```

### ❌ "Code de Gemini ne fonctionne pas"
```bash
# 1. Lis le code avec attention (ne copie pas aveuglément)
# 2. Adapte-le à ton contexte (imports, noms de variables)
# 3. Teste avec: python manage.py test
# 4. Si erreur, demande à Gemini de corriger
```

### ❌ "Gemini me donne du code TypeScript au lieu de Python"
```
Tu peux spécifier dans le prompt:
"Génère en Python, pas TypeScript"
ou
"Utilise Django, pas Node.js"
```

---

## 📞 Support rapide

**Besoin d'aide?**

1. **Dans VSCode:** Ouvre le chat Gemini et demande
2. **Documentation:** Lis GEMINI_VSCODE_SETUP.md
3. **Code:** Consulte GEMINI.md (tous les prompts)
4. **Erreurs:** Demande à Gemini de déboguer

---

## ✅ Validation - C'est prêt?

Avant de démarrer vraiment:

```
☐ Gemini installé et configuré
☐ GEMINI.md dans ton projet
☐ Premier prompt testé avec succès
☐ Tu comprends le workflow (Prompt → Copie → Teste)
☐ Tu as lu les bonnes pratiques
☐ Tu as une idée claire de l'ÉTAPE 0 à faire
```

**Si toutes les cases sont cochées: TU ES PRÊT! 🚀**

---

## 🎯 Prochaine étape: DÉMARRER L'ÉTAPE 0

Va dans **GEMINI.md** et commence par:
```
ÉTAPE 0 - PRÉPARATION
└─ Prompt 1 - Structure du projet
```

Envoie le prompt à Gemini maintenant!

**Vous avez besoin d'une pause? Pas maintenant!** ⚡

---

## 📝 Notes

- **Temps requis:** 4-5 semaines pour le projet complet
- **À faire chaque jour:** Suivre 1-2 prompts de GEMINI.md
- **Feedback:** Améliore le prompt si la réponse n'est pas bonne
- **Communauté:** Partage tes astuces avec ton équipe!

---

**Bon développement! 🚀**

*P.S. - Mets à jour la date de dernière modification chaque jour dans GEMINI.md*
