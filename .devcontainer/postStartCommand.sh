#!/bin/bash

# Script exécuté après le démarrage du devcontainer
# Mise à jour automatique des packages AI si nécessaire

LOG_FILE="/tmp/ai_packages_update.log"
LAST_UPDATE_FILE="/tmp/last_ai_update"

# Fonction de logging
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" | tee -a "$LOG_FILE"
}

# Vérifier si une mise à jour est nécessaire (une fois par jour)
should_update() {
    if [[ ! -f "$LAST_UPDATE_FILE" ]]; then
        return 0  # Première fois, mettre à jour
    fi
    
    local last_update=$(cat "$LAST_UPDATE_FILE" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local one_day=$((24 * 60 * 60))
    
    if (( current_time - last_update > one_day )); then
        return 0  # Plus d'un jour, mettre à jour
    fi
    
    return 1  # Pas besoin de mise à jour
}

# Fonction principale
main() {
    log_info "🚀 Démarrage du devcontainer - Vérification des packages AI"
    
    # Vérifier si une mise à jour est nécessaire
    if should_update; then
        log_info "📦 Mise à jour des packages AI en cours..."
        
        # Exécuter le script de mise à jour en arrière-plan
        if [[ -f "/workspaces/appia-dev/scripts/update_ai_packages.sh" ]]; then
            cd /workspaces/appia-dev
            ./scripts/update_ai_packages.sh >> "$LOG_FILE" 2>&1 &
            
            # Marquer la dernière mise à jour
            echo "$(date +%s)" > "$LAST_UPDATE_FILE"
            log_info "✅ Mise à jour des packages AI lancée en arrière-plan"
        else
            log_info "⚠️ Script de mise à jour non trouvé"
        fi
    else
        log_info "ℹ️ Packages AI à jour (vérifiés dans les dernières 24h)"
    fi
    
    log_info "🎯 Devcontainer prêt !"
}

# Exécuter seulement si ce script est appelé directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
