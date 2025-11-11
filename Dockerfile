FROM python:3.13-slim

WORKDIR /DC25_bobry

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl \
        libmagic-mgc \
        libmagic1; \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download pl_core_news_sm \
    && python -c "from sentence_transformers import SentenceTransformer; \
     SentenceTransformer('sdadas/st-polish-paraphrase-from-distilroberta')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
