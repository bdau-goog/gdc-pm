FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app.py .

# Copy classifier models (LOCAL_MODELS_DIR mode — edge-native, no GCS required)
# If models/ dir is empty or absent the pod still starts; models will be missing.
COPY models/ ./models/

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
