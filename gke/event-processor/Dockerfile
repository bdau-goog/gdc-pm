FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# EP-2: Bake all-MiniLM-L6-v2 model weights into the image at build time.
# Eliminates the 60-90s HuggingFace download on pod cold-start that EP-1
# worked around. Model is now cached in the image layer — instant startup.
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY processor.py .

CMD ["python3", "processor.py"]
