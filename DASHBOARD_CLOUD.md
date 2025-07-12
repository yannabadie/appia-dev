# 🚀 JARVYS Dashboard - Déploiement Cloud

## ☁️ Supabase Edge Functions

Le dashboard JARVYS_DEV est déployé sur **Supabase Edge Functions** pour une performance optimale et une disponibilité mondiale.

### 🌐 URL de Production

```
https://your-project-id.supabase.co/functions/v1/jarvys-dashboard
```

### 📚 API Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Dashboard principal (HTML) |
| `/api/status` | GET | Statut du système JARVYS |
| `/api/metrics` | GET | Métriques de performance |
| `/api/data` | GET | Données complètes du dashboard |
| `/api/tasks` | GET | Tâches récentes |
| `/api/chat` | POST | Chat avec l'agent JARVYS |
| `/health` | GET | Health check de l'Edge Function |

### 🔐 Configuration des Secrets

Les secrets suivants doivent être configurés dans Supabase :

```bash
# Secret d'authentification pour l'Edge Function
SPB_EDGE_FUNCTIONS=dHx8o@3?G4!QT86C
```

### 🚀 Déploiement Manuel

#### Prérequis

1. **Supabase CLI** installé :
   ```bash
   npm install -g supabase
   ```

2. **Authentification** :
   ```bash
   supabase login
   ```

3. **Variables d'environnement** :
   ```bash
   export SUPABASE_PROJECT_ID="your-project-id"
   export SPB_EDGE_FUNCTIONS="dHx8o@3?G4!QT86C"
   ```

#### Déploiement

```bash
# Déploiement automatique
./deploy-supabase.sh

# Ou déploiement manuel
supabase functions deploy jarvys-dashboard --no-verify-jwt
```

### 🤖 Déploiement Automatique (GitHub Actions)

Le déploiement est automatisé via GitHub Actions lors des push sur la branche `main`.

#### Configuration GitHub Secrets

Dans les paramètres de votre repository GitHub, ajoutez :

```
SUPABASE_SERVICE_ROLE=your-service-role-token
SUPABASE_PROJECT_ID=your-project-id  
SPB_EDGE_FUNCTIONS=dHx8o@3?G4!QT86C
```

#### Workflow

Le workflow `.github/workflows/deploy-dashboard.yml` :
- ✅ Se déclenche automatiquement sur push
- 🔧 Installe Supabase CLI
- 🚀 Déploie l'Edge Function
- 🔐 Configure les secrets
- 🧪 Teste le déploiement
- 📊 Génère un rapport

### 📊 Fonctionnalités Cloud

#### 🎯 Optimisations Edge

- **Latence ultra-faible** : Déployé sur le réseau global Supabase
- **Auto-scaling** : Gestion automatique de la charge
- **Cache intelligent** : Optimisation des réponses API
- **Monitoring intégré** : Métriques et logs automatiques

#### 🔄 Données Simulées

En environnement cloud, le dashboard utilise des données simulées réalistes :

- **Coûts API** : $1-6 quotidiens avec variations
- **Appels API** : 50-350 calls par jour
- **Tâches** : Génération automatique de tâches DevOps
- **Métriques** : Uptime, mémoire, performance

#### 🧠 Intelligence Simulée

Le chat JARVYS en mode cloud offre :

- **Réponses contextuelles** basées sur l'état du système
- **Suggestions d'optimisation** automatiques
- **Monitoring proactif** 24/7
- **Rapports de performance** en temps réel

### 🔧 Configuration Avancée

#### Variables d'Environnement

```typescript
// Dans l'Edge Function
const EDGE_FUNCTION_SECRET = Deno.env.get('SPB_EDGE_FUNCTIONS');
```

#### CORS et Sécurité

```typescript
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};
```

### 📈 Monitoring et Debug

#### Logs Supabase

```bash
# Voir les logs en temps réel
supabase functions logs jarvys-dashboard --follow
```

#### Debug Local

```bash
# Test local avant déploiement
supabase functions serve jarvys-dashboard
```

#### Health Check

```bash
# Vérifier le statut
curl https://your-project-id.supabase.co/functions/v1/jarvys-dashboard/health
```

### 🎨 Interface Utilisateur

Le dashboard cloud offre :

- **Design GitHub-inspired** avec thème sombre
- **Métriques temps réel** avec animations
- **Auto-refresh** toutes les 30 secondes
- **Responsive design** pour mobile/desktop
- **Indicateurs visuels** de statut cloud

### 🔄 Mises à Jour

#### Mise à Jour Automatique

Chaque commit sur `main` déclenche automatiquement :
1. Build de l'Edge Function
2. Tests de validation
3. Déploiement sur Supabase
4. Vérification santé
5. Notification de succès

#### Rollback

En cas de problème :

```bash
# Revenir à la version précédente
supabase functions deploy jarvys-dashboard --project-ref old-id
```

### 📞 Support

- 📧 **Issues GitHub** : Pour bugs et suggestions
- 🌐 **Dashboard Live** : Monitoring en temps réel
- 📊 **Métriques Supabase** : Performance et usage
- 🔍 **Logs** : Debug et troubleshooting

---

🎉 **JARVYS Dashboard** est maintenant déployé sur **Supabase Edge Functions** avec une performance optimale et une disponibilité mondiale !
