FROM python:3.13-slim

WORKDIR /DC25_bobry

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/* \
 && python -m spacy download pl_core_news_sm \
 && python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('sdadas/st-polish-paraphrase-from-distilroberta')"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
