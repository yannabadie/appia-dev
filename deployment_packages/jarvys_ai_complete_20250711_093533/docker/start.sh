#!/bin/bash
# Script de démarrage JARVYS_AI pour Docker Windows 11

set -e

echo "🤖 Démarrage de JARVYS_AI..."
echo "📅 $(date)"
echo "🐳 Container: $HOSTNAME"

# Configuration des logs
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export LOG_FILE="${LOG_FILE:-/app/logs/jarvys_ai.log}"

# Créer répertoire de logs si nécessaire
mkdir -p /app/logs

# Configuration audio PulseAudio
if [ -n "$PULSE_RUNTIME_PATH" ]; then
    echo "🔊 Configuration audio PulseAudio..."
    export PULSE_SERVER="unix:${PULSE_RUNTIME_PATH}/pulse/native"
fi

# Vérification santé système
echo "🔍 Vérification système..."

# Test connectivité réseau
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "✅ Connectivité réseau OK"
else
    echo "⚠️ Pas de connectivité réseau"
fi

# Test services audio
if command -v aplay >/dev/null 2>&1; then
    echo "✅ Support audio disponible"
else
    echo "⚠️ Support audio limité"
fi

# Variables d'environnement requises
required_vars=("OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️ Variable manquante: $var"
    else
        echo "✅ $var configuré"
    fi
done

# Mode de démarrage
MODE="${1:-production}"
echo "🚀 Mode: $MODE"

case "$MODE" in
    --mode)
        MODE="$2"
        ;;
    production)
        echo "🏭 Démarrage en mode production..."
        exec python -m jarvys_ai.main --config production
        ;;
    development)
        echo "🔧 Démarrage en mode développement..."
        exec python -m jarvys_ai.main --config development --debug
        ;;
    demo)
        echo "🎭 Démarrage en mode démo..."
        exec python -m jarvys_ai.main --config demo --demo-mode
        ;;
    interactive)
        echo "💬 Démarrage en mode interactif..."
        exec python -m jarvys_ai.main --interactive
        ;;
    test)
        echo "🧪 Exécution des tests..."
        exec python -m pytest tests/ -v
        ;;
    health)
        echo "🏥 Vérification santé..."
        exec python -c "
import asyncio
from jarvys_ai.main import JarvysAI

async def health_check():
    jarvys = JarvysAI({'demo_mode': True})
    try:
        await jarvys.start()
        print('✅ JARVYS_AI OK')
        return True
    except Exception as e:
        print(f'❌ JARVYS_AI KO: {e}')
        return False
    finally:
        await jarvys.stop()

result = asyncio.run(health_check())
exit(0 if result else 1)
        "
        ;;
    *)
        echo "❌ Mode inconnu: $MODE"
        echo "Modes disponibles: production, development, demo, interactive, test, health"
        exit 1
        ;;
esac
