# 🚀 Guide de Déploiement Rapide - JARVYS Dashboard

## ✅ Configuration Corrigée

La configuration a été mise à jour pour utiliser les bonnes variables d'environnement :

### 🔑 Secrets GitHub (Repository Settings > Secrets)

```
SUPABASE_ACCESS_TOKEN=your-supabase-access-token
SUPABASE_PROJECT_ID=your-project-id  ⚠️ (PROJECT_ID, pas PROJECT_REF)
SPB_EDGE_FUNCTIONS=dHx8o@3?G4!QT86C
```

### 🌐 Variables Locales (pour déploiement manuel)

```bash
export SUPABASE_ACCESS_TOKEN="your-token"
export SUPABASE_PROJECT_ID="your-project-id"
export SPB_EDGE_FUNCTIONS="dHx8o@3?G4!QT86C"
```

## 🚀 Déploiement

### Option 1: Déploiement Automatique (Recommandé)

```bash
# Commit et push - déclenche le déploiement auto
git add .
git commit -m "Deploy JARVYS Dashboard"
git push origin main
```

### Option 2: Déploiement Manuel

```bash
# Rendre le script exécutable
chmod +x deploy-supabase.sh

# Déployer
./deploy-supabase.sh
```

## 🧪 Validation

### Valider la Configuration

```bash
# Vérifier que tous les fichiers utilisent PROJECT_ID
python3 validate_project_config.py

# Vérifier la configuration des secrets
python3 validate_secret_config.py
```

### Tester le Dashboard Déployé

```bash
# Health check
curl https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard/health

# API Status
curl https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard/api/status

# Dashboard (dans le navigateur)
open https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard
```

## 📊 URLs du Dashboard

Remplacez `YOUR-PROJECT-ID` par votre vrai project ID Supabase :

- **Dashboard:** https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard
- **API Status:** https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard/api/status  
- **Métriques:** https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard/api/metrics
- **Health:** https://YOUR-PROJECT-ID.supabase.co/functions/v1/jarvys-dashboard/health

## 🔧 Dépannage

### Erreur "PROJECT_REF not found"

✅ **Résolu** - Tous les fichiers utilisent maintenant `SUPABASE_PROJECT_ID`

### Secret non configuré

```bash
# Configurer manuellement dans Supabase
supabase secrets set SPB_EDGE_FUNCTIONS="dHx8o@3?G4!QT86C" --project-ref YOUR-PROJECT-ID
```

### Logs de déploiement

```bash
# Voir les logs de l'Edge Function
supabase functions logs jarvys-dashboard --follow
```

## ✅ Checklist de Déploiement

- [ ] Secrets GitHub configurés avec PROJECT_ID (pas PROJECT_REF)
- [ ] Validation config passée (`validate_project_config.py`)
- [ ] Edge Function déployée
- [ ] Secret SPB_EDGE_FUNCTIONS configuré
- [ ] Health check OK
- [ ] Dashboard accessible

---

🎉 **JARVYS Dashboard** est prêt pour le déploiement sur **Supabase Edge Functions** !
