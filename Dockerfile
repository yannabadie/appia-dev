FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Only run pip if the file exists; avoids hard‑fail in early prototyping
RUN test -f requirements.txt && pip install --no-cache-dir -r requirements.txt || \
    echo "No requirements.txt – skipping pip install"

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
