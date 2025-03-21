FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY back-end/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY back-end/src /app/src

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

CMD ["uvicorn", "src.main.main:app", "--host", "0.0.0.0", "--port", "8000"]