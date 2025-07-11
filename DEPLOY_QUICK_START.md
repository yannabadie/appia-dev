# 🚀 Guide de Déploiement Rapide - JARVYS Dashboard

## 🔑 Configuration du Secret SPB_EDGE_FUNCTIONS

### Valeur du Secret
```
SPB_EDGE_FUNCTIONS=dHx8o@3?G4!QT86C
```

## 📝 Étapes de Configuration

### 1. 🐙 Configuration GitHub Secrets

1. **Accédez aux paramètres du repository :**
   ```
   https://github.com/YOUR_USERNAME/appia-dev/settings/secrets/actions
   ```

2. **Ajoutez les secrets suivants :**
   ```
   Name: SPB_EDGE_FUNCTIONS
   Value: dHx8o@3?G4!QT86C
   
   Name: SUPABASE_ACCESS_TOKEN
   Value: [Votre token Supabase]
   
   Name: SUPABASE_PROJECT_REF
   Value: [Votre project ref Supabase]
   ```

### 2. 🌐 Configuration Supabase

#### Via CLI (Recommandé)
```bash
# Connexion à Supabase
supabase login

# Configuration du secret
supabase secrets set SPB_EDGE_FUNCTIONS="dHx8o@3?G4!QT86C" --project-ref YOUR_PROJECT_REF
```

#### Via Interface Web
1. Connectez-vous à https://supabase.com/dashboard
2. Sélectionnez votre projet
3. Allez dans **Settings** > **Edge Functions**
4. Ajoutez le secret :
   - **Name:** `SPB_EDGE_FUNCTIONS`
   - **Value:** `dHx8o@3?G4!QT86C`

### 3. 🚀 Déploiement

#### Déploiement Automatique (Recommandé)
```bash
# Commit et push pour déclencher le déploiement automatique
git add .
git commit -m "Configure SPB_EDGE_FUNCTIONS secret"
git push origin main
```

#### Déploiement Manuel
```bash
# Avec le script fourni
./deploy-supabase.sh

# Ou directement avec Supabase CLI
supabase functions deploy jarvys-dashboard --no-verify-jwt
```

## 🧪 Vérification du Déploiement

### Tests Automatiques
Le workflow GitHub Actions exécute automatiquement :
- ✅ Test health check
- ✅ Test API status
- ✅ Validation des endpoints

### Tests Manuels
```bash
# Health check
curl https://YOUR_PROJECT_REF.supabase.co/functions/v1/jarvys-dashboard/health

# API Status
curl https://YOUR_PROJECT_REF.supabase.co/functions/v1/jarvys-dashboard/api/status

# Dashboard principal
curl https://YOUR_PROJECT_REF.supabase.co/functions/v1/jarvys-dashboard/
```

## 📊 URLs du Dashboard

Une fois déployé, votre dashboard sera disponible à :

### 🌐 Dashboard Principal
```
https://YOUR_PROJECT_REF.supabase.co/functions/v1/jarvys-dashboard/
```

### 📚 API Endpoints
```
GET  /api/status     - Statut du système JARVYS
GET  /api/metrics    - Métriques de performance  
GET  /api/data       - Données complètes du dashboard
GET  /api/tasks      - Tâches récentes
POST /api/chat       - Chat avec l'agent JARVYS
GET  /health         - Health check
```

## 🔧 Dépannage

### Erreur "Secret non configuré"
```bash
# Vérifiez la configuration
supabase secrets list --project-ref YOUR_PROJECT_REF

# Reconfigurez si nécessaire
supabase secrets set SPB_EDGE_FUNCTIONS="dHx8o@3?G4!QT86C"
```

### Erreur de déploiement
```bash
# Vérifiez les logs
supabase functions logs jarvys-dashboard --follow

# Redéployez
supabase functions deploy jarvys-dashboard --no-verify-jwt
```

### GitHub Actions en échec
1. Vérifiez que tous les secrets sont configurés dans GitHub
2. Consultez les logs de l'action
3. Relancez le workflow si nécessaire

## 🎉 Statut de Configuration

✅ **Secret SPB_EDGE_FUNCTIONS configuré:** `dHx8o@3?G4!QT86C`  
✅ **Edge Function prête:** `/supabase/functions/jarvys-dashboard/index.ts`  
✅ **Workflow GitHub Actions:** `.github/workflows/deploy-dashboard.yml`  
✅ **Script de déploiement:** `deploy-supabase.sh`  
✅ **Documentation complète:** `DASHBOARD_CLOUD.md`  

## 📞 Support

En cas de problème :
1. 📋 Consultez les logs de déploiement
2. 🔍 Vérifiez la configuration des secrets
3. 🧪 Testez les endpoints manuellement
4. 📚 Consultez la documentation complète dans `DASHBOARD_CLOUD.md`

---

🚀 **JARVYS Dashboard** est maintenant prêt pour le déploiement cloud avec Supabase Edge Functions !
