from __future__ import annotations

from typing import List, Tuple

import re
import spacy
from sentence_transformers import SentenceTransformer, util


class SynonymRecognizer:
    _nlp = None
    _model = None

    @classmethod
    def _get_nlp(cls):
        if cls._nlp is None:
            cls._nlp = spacy.load("pl_core_news_sm")
        return cls._nlp

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer(
                "sdadas/st-polish-paraphrase-from-distilroberta"
            )
        return cls._model

    def __init__(self, text: str, threshold: float = 0.7):
        self._nlp = self._get_nlp()
        self._model = self._get_model()
        self._threshold = threshold

        self._filtered_tokens: List[Tuple[str, str]] = self._preprocess_text(text)

        if self._filtered_tokens:
            self._tokens_embedding = self._model.encode(
                [token[1] for token in self._filtered_tokens],
                convert_to_tensor=True,
            )
        else:
            self._tokens_embedding = None

    def _preprocess_text(self, text: str) -> List[Tuple[str, str]]:
        cleaned_text = " ".join(
            [re.sub(r"[^\w\d\s]", "", token.lower()) for token in text.split()]
        )
        doc = self._nlp(cleaned_text)

        return [
            (token.text, token.lemma_)
            for token in doc
            if not token.is_stop
            and not token.is_punct
            and not token.is_space
            and not token.is_digit
        ]

    def find_synonyms(self, word: str) -> List[str]:
        if self._tokens_embedding is None or not self._filtered_tokens:
            return []

        word_embedding = self._model.encode(word, convert_to_tensor=True)
        similarities = util.cos_sim(word_embedding, self._tokens_embedding)[0]
        sorted_indices = similarities.argsort(descending=True)

        possible_synonyms: List[str] = []

        for idx in sorted_indices:
            sim = float(similarities[idx])
            if sim >= self._threshold:
                possible_synonyms.append(self._filtered_tokens[int(idx)][0])
            else:
                break

        return possible_synonyms
