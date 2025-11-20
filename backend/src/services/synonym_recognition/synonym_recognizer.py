from typing import List
import spacy
import re
from sentence_transformers import SentenceTransformer, util


class SynonymRecognizer:
    def __init__(self, text: str, threshold: float = 0.7):
        self.__nlp = spacy.load('pl_core_news_sm')
        self.__filtered_tokens = self.__preprocess_text(text)
        self.__model = SentenceTransformer('sdadas/st-polish-paraphrase-from-distilroberta')
        self.__tokens_embedding = self.__model.encode([token[1] for token in self.__filtered_tokens])
        self.__threshold = threshold

    def __preprocess_text(self, text: str) -> list[tuple[str, str]]:
        cleaned_text = ' '.join([re.sub(r'[^\w\d\s]', '', token.lower()) for token in text.split()])

        doc = self.__nlp(cleaned_text)

        return [(token.text, token.lemma_) for token in doc if
                not token.is_stop and not token.is_punct and not token.is_space and not token.is_digit]

    def find_synonyms(self, word: str) -> List[str]:
        word_embedding = self.__model.encode(word)
        similarities = util.cos_sim(word_embedding, self.__tokens_embedding)[0]
        sorted_indices = similarities.argsort(descending=True)

        possible_synonyms = []

        for idx in sorted_indices:
            if similarities[idx] >= self.__threshold:
                possible_synonyms.append(self.__filtered_tokens[idx][0])

        return possible_synonyms
