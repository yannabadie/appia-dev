#!/bin/bash
# Test du dashboard avec authentification

echo "🔐 Test d'accès au dashboard JARVYS_DEV"
echo "========================================="

DASHBOARD_URL="https://kzcswopokvknxmxczilu.supabase.co/functions/v1/jarvys-dashboard"
SUPABASE_KEY="${SUPABASE_KEY:-}"

echo "📡 URL: $DASHBOARD_URL"

# Test sans authentification (devrait échouer)
echo -e "\n1. 🚫 Test sans authentification:"
curl -s "$DASHBOARD_URL" | jq -r '.' 2>/dev/null || curl -s "$DASHBOARD_URL"

# Test avec token en paramètre
if [ -n "$SUPABASE_KEY" ]; then
    echo -e "\n2. ✅ Test avec token:"
    curl -s "$DASHBOARD_URL?token=$SUPABASE_KEY" | head -20
else
    echo -e "\n2. ⚠️  Variable SUPABASE_KEY non définie"
fi

# Test avec header Authorization
echo -e "\n3. 🔑 Test avec header Authorization:"
curl -s -H "Authorization: Bearer $(echo $SUPABASE_KEY)" "$DASHBOARD_URL" | head -20

echo -e "\n📋 Pour accéder au dashboard:"
echo "   $DASHBOARD_URL?token=YOUR_SUPABASE_KEY"
