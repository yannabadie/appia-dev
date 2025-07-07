FROM python:3.12-slim
WORKDIR /app
# Copy the entire repository into the container
COPY . /app

# Install dependencies only if requirements.txt is present in /app
RUN if [ -f /app/requirements.txt ]; then \
        pip install --no-cache-dir -r /app/requirements.txt ; \
    else \
        echo "Warning: /app/requirements.txt not found – skipping pip install"; \
    fi

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
