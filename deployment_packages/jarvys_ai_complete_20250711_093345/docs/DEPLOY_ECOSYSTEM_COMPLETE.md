# 🚀 JARVYS Ecosystem - Guide de Déploiement Complet

Ce guide couvre le déploiement de l'écosystème JARVYS complet : JARVYS_DEV (cloud) + JARVYS_AI (local) + système de fallback.

## 🏗️ Architecture Complète

```
🌐 CLOUD (JARVYS_DEV)
├── 📊 Dashboard Supabase Edge Functions
├── 🤖 GitHub Actions (Agent principal)
├── ☁️ Cloud Run (Fallback)
└── 📡 API Endpoints

🏠 LOCAL (JARVYS_AI)
├── 🤖 Agent Digital Twin
├── 🎤 Interface Vocale
├── 📧 Email Manager
├── 📁 File Manager
├── ☁️ Cloud Manager
├── 🔄 Continuous Improvement
└── 🚨 Fallback Engine
```

## 🚀 Déploiement Cloud (JARVYS_DEV)

### 1. Dashboard Supabase (Déjà déployé)

✅ **Status**: Opérationnel sur `https://kzcswopokvknxmxczilu.supabase.co`

```bash
# Vérifier le dashboard
curl https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/health

# Tester les endpoints
curl https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/api/status
```

### 2. GitHub Actions (Principal)

✅ **Status**: Configuré dans `.github/workflows/jarvys-cloud.yml`

**Secrets configurés** :
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_ACCESS_TOKEN`
- `SUPABASE_PROJECT_ID`
- `SUPABASE_SERVICE_ROLE`

### 3. Cloud Run (Fallback)

Pour configurer le fallback Cloud Run :

```bash
# 1. Activer les APIs nécessaires
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 2. Créer le service Cloud Run de fallback
gcloud run deploy jarvys-fallback-service \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10

# 3. Obtenir l'URL du service
gcloud run services describe jarvys-fallback-service \
  --platform managed \
  --region europe-west1 \
  --format 'value(status.url)'
```

## 🏠 Déploiement Local (JARVYS_AI)

### 1. Installation Windows 11

**Prérequis** :
- Windows 11 (21H2+)
- WSL 2 activé
- Docker Desktop
- Git pour Windows

```powershell
# Cloner le repository
git clone https://github.com/yannabadie/appia-dev.git
cd appia-dev

# Configurer l'environnement
copy .env.example .env
# Éditer .env avec vos clés API
```

### 2. Configuration .env

```env
# Core APIs
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://kzcswopokvknxmxczilu.supabase.co
SUPABASE_KEY=your-supabase-key

# Email (optionnel)
GMAIL_EMAIL=your.email@gmail.com
GMAIL_PASSWORD=your-app-password
OUTLOOK_EMAIL=your.email@outlook.com

# Cloud (optionnel)
GOOGLE_CLOUD_PROJECT=your-gcp-project
AZURE_SUBSCRIPTION_ID=your-azure-sub

# Configuration
ENVIRONMENT=local
DEMO_MODE=false
VOICE_ENABLED=true
AUTO_IMPROVE=true
```

### 3. Démarrage Docker

```powershell
# Mode production complet
docker-compose -f docker-compose.windows.yml up -d

# Mode développement
docker-compose -f docker-compose.windows.yml up jarvys_ai

# Mode démo (sans clés API)
docker run -it --rm \
  -p 8000:8000 \
  -e DEMO_MODE=true \
  jarvys_ai:latest --mode demo
```

### 4. Test de Fonctionnement

```powershell
# Test complet automatisé
python test_jarvys_ai_complete.py

# Test API
curl http://localhost:8000/health

# Test commande
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour JARVYS"}'
```

## 🔗 Intégration Cloud ↔ Local

### 1. Connexion Dashboard

JARVYS_AI local se connecte automatiquement au dashboard cloud :

```python
# Intégration automatique
from jarvys_ai.dashboard_integration import setup_dashboard_integration

# La connexion se fait automatiquement au démarrage
```

### 2. Synchronisation Continue

- **Métriques** : JARVYS_AI envoie ses métriques au dashboard (5 min)
- **Améliorations** : JARVYS_AI reçoit les updates de JARVYS_DEV (30 min)
- **Commands** : Le dashboard peut envoyer des commandes à JARVYS_AI

### 3. Système de Fallback

Le système bascule automatiquement :

```
GitHub Actions quotas épuisés
           ↓
    Détection automatique
           ↓
     Activation Cloud Run
           ↓
    Redirection du trafic
           ↓
    Notification utilisateur
```

## 🧪 Tests et Validation

### 1. Test Dashboard Cloud

```bash
# Test santé dashboard
curl https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/health

# Test endpoints API
curl https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/api/status
curl https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/api/metrics
curl https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/api/tasks
```

### 2. Test JARVYS_AI Local

```powershell
# Test complet (tous composants)
python test_jarvys_ai_complete.py

# Test spécifique interface vocale
docker exec -it jarvys_ai_main python -c "
from jarvys_ai.extensions.voice_interface import VoiceInterface
import asyncio
async def test():
    voice = VoiceInterface({'demo_mode': True})
    await voice.initialize()
    await voice.speak('JARVYS AI est prêt')
asyncio.run(test())
"
```

### 3. Test Fallback

```python
# Test manuel du fallback
from jarvys_ai.fallback_engine import FallbackEngine
import asyncio

async def test_fallback():
    engine = FallbackEngine({'demo_mode': True})
    await engine.initialize()
    result = await engine.force_fallback_test()
    print(f"Fallback test: {result['test_successful']}")

asyncio.run(test_fallback())
```

## 📊 Monitoring et Surveillance

### 1. Dashboard Principal

**URL** : https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard/

**Métriques surveillées** :
- État des agents (cloud + local)
- Coûts API en temps réel  
- Performance et réponse
- Tâches en cours
- Système de fallback

### 2. Logs Locaux

```powershell
# Logs JARVYS_AI
docker logs jarvys_ai_main -f

# Logs spécifiques
docker exec -it jarvys_ai_main tail -f /app/logs/jarvys_ai.log
```

### 3. Métriques Prometheus

**URL** : http://localhost:9090

Métriques disponibles :
- CPU/Memory usage
- Response times
- Error rates
- Voice commands
- Email operations

## 🚨 Résolution de Problèmes

### 1. Problèmes Cloud

```bash
# Vérifier Supabase
supabase status

# Redéployer dashboard
supabase functions deploy jarvys-dashboard

# Vérifier GitHub Actions
gh workflow list
gh run list
```

### 2. Problèmes Local

```powershell
# Redémarrer services
docker-compose -f docker-compose.windows.yml restart

# Vérifier ressources
docker stats

# Debug mode
docker-compose -f docker-compose.windows.yml up jarvys_ai --remove-orphans
```

### 3. Problèmes Audio/Vocal

```powershell
# Vérifier périphériques audio
docker exec -it jarvys_ai_main aplay -l

# Test microphone
docker exec -it jarvys_ai_main python -c "
import speech_recognition as sr
print('Microphones:', sr.Microphone.list_microphone_names())
"

# Redémarrer PulseAudio
docker exec -it jarvys_ai_main pulseaudio --kill
docker exec -it jarvys_ai_main pulseaudio --start
```

## 🔄 Mises à Jour

### 1. Mise à jour Cloud

```bash
# Via GitHub Actions (automatique lors des commits)
git push origin main

# Manuel via Supabase CLI
supabase functions deploy jarvys-dashboard
```

### 2. Mise à jour Local

```powershell
# Arrêter services
docker-compose -f docker-compose.windows.yml down

# Mettre à jour code
git pull origin main

# Reconstruire
docker-compose -f docker-compose.windows.yml build --no-cache

# Redémarrer
docker-compose -f docker-compose.windows.yml up -d
```

### 3. Mises à jour Automatiques

JARVYS_AI se met à jour automatiquement via le système d'amélioration continue :

- Détection updates depuis JARVYS_DEV
- Application automatique avec sauvegarde
- Rollback en cas d'échec
- Rapport à JARVYS_DEV

## 🎯 Utilisation Quotidienne

### 1. Commandes Vocales

```
"Hey JARVYS, lis mes emails"
"Hey JARVYS, quel est mon planning aujourd'hui"
"Hey JARVYS, envoie un message à Marie"
"Hey JARVYS, status cloud"
"Hey JARVYS, cherche le fichier projet"
```

### 2. Interface Web

- **Dashboard** : http://localhost:8001
- **API** : http://localhost:8000
- **Monitoring** : http://localhost:9090

### 3. Commandes CLI

```powershell
# Status complet
docker exec -it jarvys_ai_main python -c "
from jarvys_ai.main import JarvysAI
import asyncio
async def status():
    jarvys = JarvysAI({'demo_mode': True})
    print(jarvys.get_status())
asyncio.run(status())
"

# Forcer synchronisation
docker exec -it jarvys_ai_main python -c "
from jarvys_ai.continuous_improvement import ContinuousImprovement
import asyncio
async def sync():
    ci = ContinuousImprovement({'demo_mode': True})
    await ci.initialize()
    await ci.sync_with_jarvys_dev()
asyncio.run(sync())
"
```

## 🎉 Déploiement Réussi !

Si vous arrivez jusqu'ici, vous avez :

✅ **JARVYS_DEV** opérationnel sur Supabase  
✅ **JARVYS_AI** fonctionnel sur Windows 11  
✅ **Système de fallback** Cloud Run configuré  
✅ **Intégration complète** cloud ↔ local  
✅ **Interface vocale** activée  
✅ **Amélioration continue** en place  

**🤖 Bienvenue dans l'écosystème JARVYS !**

---

**Support** : En cas de problème, consultez les logs ou créez une issue sur GitHub.

**Version** : 1.0.0 - Digital Twin de Yann Abadie  
**Créé par** : JARVYS_DEV Agent DevOps Autonome
