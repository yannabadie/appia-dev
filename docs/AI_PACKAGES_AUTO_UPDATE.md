# 🤖 Système de Mise à Jour Automatique des Packages AI

## Vue d'ensemble

Le devcontainer `appia-dev` est configuré pour maintenir automatiquement
les dernières versions des packages d'intelligence artificielle essentiels :

- **anthropic** (≥0.57.1)
- **google-generativeai** (≥0.8.5)
- **openai** (dernière version)

## Architecture du Système

### 🔧 Composants

#### 1. Script Principal : `scripts/update_ai_packages.sh`

- Mise à jour vers les dernières versions disponibles
- Vérification des versions actuelles et nouvelles
- Mise à jour du fichier `poetry.lock`
- Logs détaillés avec horodatage
- Support complet Poetry + pip

#### 2. Configuration DevContainer : `.devcontainer/devcontainer.json`

```json
{
  "postCreateCommand": "bash -l /workspaces/appia-dev/.devcontainer/setup.sh",
  "postStartCommand": "bash -l /workspaces/appia-dev/.devcontainer/postStartCommand.sh"
}
```

#### 3. Script de Démarrage : `.devcontainer/postStartCommand.sh`

- Vérification quotidienne automatique (24h)
- Mise à jour en arrière-plan
- Logs persistants dans `/tmp/ai_packages_update.log`
- Marquage temporel des dernières mises à jour

#### 4. Configuration des Dépendances

**pyproject.toml** et **requirements.txt** :

```toml
[tool.poetry.dependencies]
anthropic = ">=0.57.1"
google-generativeai = ">=0.8.5"
openai = "*"  # Dernière version
```

## 🚀 Fonctionnement

### Démarrage du DevContainer

1. **PostCreate** : Installation initiale des dépendances
2. **PostStart** : Vérification automatique des mises à jour (si > 24h)
3. **Logs** : Toutes les opérations sont tracées

### Mise à Jour Manuelle

```bash
# Mise à jour immédiate
./scripts/update_ai_packages.sh

# Vérification des logs
cat /tmp/ai_packages_update.log
```

### Fréquence des Mises à Jour

- **Automatique** : Quotidienne (au démarrage du container)
- **Manuel** : À la demande via script
- **Poetry Lock** : Mis à jour automatiquement après chaque changement

## 📊 Monitoring

### Vérification des Versions

```bash
# Versions actuelles
pip list | grep -E "(anthropic|google-generativeai|openai)"

# Test d'import
python -c "import anthropic, google.generativeai, openai; \
print('✅ Tous les packages AI fonctionnels')"
```

### Logs de Mise à Jour

```bash
# Logs complets
cat /tmp/ai_packages_update.log

# Dernière mise à jour
cat /tmp/last_ai_update
```

## 🔄 Processus de Mise à Jour

### 1. Détection des Nouvelles Versions

Le script vérifie PyPI pour les dernières versions disponibles et
compare avec les versions installées.

### 2. Installation

```bash
pip install --upgrade anthropic google-generativeai openai
```

### 3. Vérification Post-Installation

Test d'import et affichage des nouvelles versions.

### 4. Mise à Jour de Poetry

```bash
poetry lock
```

## 🎯 Avantages

- ✅ **Sécurité** : Dernières versions avec correctifs de sécurité
- ✅ **Performance** : Améliorations et optimisations récentes
- ✅ **Compatibilité** : Nouvelles fonctionnalités des APIs
- ✅ **Automatisation** : Aucune intervention manuelle requise
- ✅ **Traçabilité** : Logs complets de toutes les opérations

## 🛠️ Maintenance

### Désactiver les Mises à Jour Automatiques

Supprimer ou commenter la ligne `postStartCommand` dans `devcontainer.json` :

```json
// "postStartCommand": "bash -l /workspaces/appia-dev/.devcontainer/postStartCommand.sh",
```

### Forcer une Mise à Jour

```bash
# Réinitialiser le marqueur temporel
rm /tmp/last_ai_update

# Relancer la vérification
./.devcontainer/postStartCommand.sh
```

### Versions Spécifiques

Modifier `pyproject.toml` pour contraindre une version :

```toml
anthropic = "==0.57.1"  # Version exacte
google-generativeai = "~=0.8.0"  # Version compatible
```

## 📝 Notes Importantes

- Les mises à jour s'exécutent en arrière-plan pour ne pas bloquer
  le démarrage
- Le système respecte les contraintes de version définies dans
  `pyproject.toml`
- Les logs sont conservés entre les redémarrages du container
- La fréquence peut être ajustée en modifiant la logique dans
  `postStartCommand.sh`

## 🚨 Dépannage

### Package Non Mis à Jour

1. Vérifier les logs : `cat /tmp/ai_packages_update.log`
2. Tester manuellement : `./scripts/update_ai_packages.sh`
3. Vérifier les contraintes dans `pyproject.toml`

### Problème d'Import

```bash
# Réinstaller le package problématique
pip install --force-reinstall google-generativeai

# Vérifier l'environnement Python
which python
python -c "import sys; print(sys.path)"
```

### Réinitialisation Complète

```bash
# Supprimer l'environnement virtuel
rm -rf .venv

# Relancer l'installation
poetry install
poetry run pip install --upgrade anthropic google-generativeai openai
```
