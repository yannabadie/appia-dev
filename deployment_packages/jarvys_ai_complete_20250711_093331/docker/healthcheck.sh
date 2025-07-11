#!/bin/bash
# Health check pour JARVYS_AI Docker

set -e

# Vérifier si le processus principal est actif
if ! pgrep -f "python.*jarvys_ai" > /dev/null; then
    echo "❌ Processus JARVYS_AI non trouvé"
    exit 1
fi

# Test rapide d'importation
python -c "
try:
    from jarvys_ai import JarvysAI
    print('✅ Import JARVYS_AI OK')
except Exception as e:
    print(f'❌ Import JARVYS_AI KO: {e}')
    exit(1)
" || exit 1

# Vérifier fichiers de logs
if [ -f "/app/logs/jarvys_ai.log" ]; then
    # Vérifier si les logs sont récents (moins de 5 minutes)
    if [ $(find /app/logs/jarvys_ai.log -mmin -5 2>/dev/null | wc -l) -eq 1 ]; then
        echo "✅ Logs récents détectés"
    else
        echo "⚠️ Logs anciens (possiblement bloqué)"
        exit 1
    fi
else
    echo "⚠️ Fichier de log manquant"
fi

# Test connectivité réseau basique
if command -v curl >/dev/null 2>&1; then
    if curl -s --max-time 5 https://google.com >/dev/null; then
        echo "✅ Connectivité réseau OK"
    else
        echo "⚠️ Problème connectivité réseau"
    fi
fi

echo "✅ Health check réussi"
exit 0
