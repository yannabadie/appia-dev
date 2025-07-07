FROM python:3.12-slim
WORKDIR /app
COPY . /app

# Installe seulement si le fichier existe à /app
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt ; \
    else \
        echo "⚠️  No requirements.txt found – skipping pip install"; \
    fi

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
