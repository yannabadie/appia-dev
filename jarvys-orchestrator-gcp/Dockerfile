# 🤖 DOCKERFILE - JARVYS Orchestrator GCP
# =======================================
#
# Container optimisé pour Cloud Run avec:
# - Image Python slim pour performance  
# - Multi-stage build pour taille minimale
# - Health checks et monitoring intégrés
# - Configuration GCP native

FROM python:3.12-slim as builder

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage de production
FROM python:3.12-slim

# Créer utilisateur non-root pour sécurité
RUN useradd --create-home --shell /bin/bash jarvys

# Copier les packages Python du builder
COPY --from=builder /root/.local /home/jarvys/.local

# Copier le code source  
WORKDIR /app
COPY --chown=jarvys:jarvys . .

# Configuration PATH pour packages utilisateur
ENV PATH=/home/jarvys/.local/bin:$PATH

# Variables d'environnement Cloud Run
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Port Cloud Run (configuré automatiquement)
ENV PORT=8080

# Exposer le port
EXPOSE 8080

# Changer vers utilisateur non-root
USER jarvys

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Commande de démarrage
CMD ["python", "grok_orchestrator_gcp.py"]
