# 🤖 JARVYS_AI - Guide Windows 11 Docker

Ce guide vous permet d'installer et exécuter JARVYS_AI sur Windows 11 avec
Docker Desktop et support vocal complet.

## 🚀 Installation Rapide

### 1. Prérequis Windows 11

Assurez-vous d'avoir :

- ✅ Windows 11 (version 21H2 ou plus récente)
- ✅ WSL 2 activé (`wsl --install`)
- ✅ Docker Desktop pour Windows (avec WSL 2 backend)
- ✅ Git pour Windows
- ✅ PowerShell 7+ (recommandé)

### 2. Installation Docker Desktop

```powershell
# Télécharger et installer Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Vérifier l'installation
docker --version
docker-compose --version
```

### 3. Configuration Audio (Important)

Pour l'interface vocale, configurez PulseAudio sur WSL :

```bash
# Dans WSL2
sudo apt update && sudo apt install -y pulseaudio

# Démarrer PulseAudio
pulseaudio --start
```

### 4. Clonage et Configuration

```powershell
# Cloner le repository
git clone https://github.com/yannabadie/appia-dev.git
cd appia-dev

# Copier le fichier d'environnement
copy .env.example .env

# Éditer les variables d'environnement
notepad .env
```

### 5. Configuration .env

Éditez le fichier `.env` avec vos clés :

```env
# API Keys (obligatoires)
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Base de données locale
DB_PASSWORD=your-secure-password

# Configuration Windows
USERPROFILE=C:\Users\YourUsername
```

## 🎯 Démarrage JARVYS_AI

### Mode Production (Recommandé)

```powershell
# Démarrer tous les services
docker-compose -f docker-compose.windows.yml up -d

# Vérifier le statut
docker-compose -f docker-compose.windows.yml ps

# Voir les logs
docker-compose -f docker-compose.windows.yml logs -f jarvys_ai
```

### Mode Développement

```powershell
# Démarrer en mode dev avec logs en temps réel
docker-compose -f docker-compose.windows.yml up jarvys_ai
```

### Mode Démo (Sans clés API)

```powershell
# Démarrer en mode démo avec données simulées
docker run -it --rm \
  -p 8000:8000 \
  -e DEMO_MODE=true \
  jarvys_ai:latest --mode demo
```

## 🎤 Test Interface Vocale

### 1. Vérification Audio

```powershell
# Test depuis le container
docker exec -it jarvys_ai_main python -c "
import pyttsx3
engine = pyttsx3.init()
engine.say('Hello, JARVYS AI is ready')
engine.runAndWait()
"
```

### 2. Test Reconnaissance Vocale

```powershell
# Test reconnaissance vocale
docker exec -it jarvys_ai_main python -c "
import speech_recognition as sr
r = sr.Recognizer()
print('Microphone test OK' if sr.Microphone.list_microphone_names() else 'No microphone')
"
```

## 📧 Configuration Email

### Gmail

1. Activez l'authentification à 2 facteurs
2. Générez un mot de passe d'application
3. Ajoutez à votre `.env` :

```env
GMAIL_EMAIL=your.email@gmail.com
GMAIL_PASSWORD=your-app-password
```

### Outlook/Office 365

```env
OUTLOOK_EMAIL=your.email@outlook.com
OUTLOOK_CLIENT_ID=your-azure-app-id
OUTLOOK_CLIENT_SECRET=your-azure-secret
```

## ☁️ Intégration Cloud

### Google Cloud Platform

```env
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/app/config/gcp-key.json
```

### Microsoft Azure

```env
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-app-id
AZURE_CLIENT_SECRET=your-secret
```

## 🔧 Commandes Utiles

### Gestion Container

```powershell
# Redémarrer JARVYS_AI
docker-compose -f docker-compose.windows.yml restart jarvys_ai

# Mise à jour de l'image
docker-compose -f docker-compose.windows.yml pull
docker-compose -f docker-compose.windows.yml up -d

# Accès shell dans le container
docker exec -it jarvys_ai_main bash

# Voir l'utilisation des ressources
docker stats jarvys_ai_main
```

### Sauvegarde/Restauration

```powershell
# Sauvegarder les données
docker run --rm -v jarvys_data:/data -v ${PWD}:/backup alpine \
  tar czf /backup/jarvys-backup.tar.gz /data

# Restaurer les données
docker run --rm -v jarvys_data:/data -v ${PWD}:/backup alpine \
  tar xzf /backup/jarvys-backup.tar.gz -C /
```

## 🌐 Accès Interfaces

Une fois démarré, JARVYS_AI est accessible via :

- 🖥️ **API principale** : <http://localhost:8000>
- 📊 **Dashboard** : <http://localhost:8001>
- 📈 **Monitoring** : <http://localhost:9090> (Prometheus)
- 💾 **Base de données** : localhost:5432 (PostgreSQL)
- 🔄 **Cache** : localhost:6379 (Redis)

## 🎯 Premiers Tests

### 1. Test API

```powershell
# Test de santé
curl http://localhost:8000/health

# Test commande simple
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour JARVYS"}'
```

### 2. Test Interface Vocale

```powershell
# Démarrer l'écoute vocale
docker exec -it jarvys_ai_main python -c "
import asyncio
from jarvys_ai.main import JarvysAI

async def test_voice():
    jarvys = JarvysAI()
    await jarvys.start()
    # Dire 'Hey JARVYS, quel temps fait-il ?'
    await jarvys.extensions['voice'].start_listening()

asyncio.run(test_voice())
"
```

## 🚨 Dépannage

### Problèmes Audio

```powershell
# Vérifier les périphériques audio
docker exec -it jarvys_ai_main aplay -l

# Redémarrer PulseAudio
docker exec -it jarvys_ai_main pulseaudio --kill
docker exec -it jarvys_ai_main pulseaudio --start
```

### Problèmes Réseau

```powershell
# Test connectivité
docker exec -it jarvys_ai_main ping google.com

# Vérifier ports
netstat -an | findstr ":8000"
```

### Problèmes Permissions

```powershell
# Exécuter PowerShell en administrateur
# Redémarrer Docker Desktop
# Vérifier WSL 2 : wsl --status
```

## 📋 Configuration Avancée

### Variables d'Environnement Complètes

```env
# Core
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# IA et APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# Base de données
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
DB_PASSWORD=secure_password

# Email
GMAIL_EMAIL=...
GMAIL_PASSWORD=...
OUTLOOK_EMAIL=...
OUTLOOK_CLIENT_ID=...

# Cloud
GOOGLE_CLOUD_PROJECT=...
AZURE_SUBSCRIPTION_ID=...
AWS_ACCESS_KEY_ID=...

# Interface
VOICE_ENABLED=true
DEMO_MODE=false
WEB_UI_ENABLED=true

# Sécurité
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-32-char-key
```

## 🔄 Mise à Jour

```powershell
# Arrêter les services
docker-compose -f docker-compose.windows.yml down

# Mettre à jour le code
git pull origin main

# Reconstruire l'image
docker-compose -f docker-compose.windows.yml build --no-cache

# Redémarrer
docker-compose -f docker-compose.windows.yml up -d
```

---

**🎉 Félicitations !** JARVYS_AI est maintenant opérationnel sur votre
Windows 11.

Pour obtenir de l'aide :
`docker exec -it jarvys_ai_main python -m jarvys_ai.main --help`

**🤖 Dites simplement** : *"Hey JARVYS, aide-moi"* et votre assistant
numérique répondra !
