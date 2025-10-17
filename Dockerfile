FROM python:3.13-slim

WORKDIR /DC25_bobry

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
