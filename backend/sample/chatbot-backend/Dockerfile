# Use a slim Python 3.11 image
FROM python:3.11-slim

# Set environment variables (Updated to modern key=value format)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/user
ENV PATH="/home/user/.local/bin:${PATH}"

# 1. Create a non-root user for Hugging Face
RUN useradd -m -u 1000 user
WORKDIR $HOME/app

# 2. Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy requirements and install
# We upgrade pip first as requested by your logs
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. Pre-download your embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 5. Copy the rest of the application
COPY --chown=user . .

# 6. Switch to the non-root user
USER user

# 7. Hugging Face standard port
EXPOSE 7860

# 8. Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]