FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd -m appuser

COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
