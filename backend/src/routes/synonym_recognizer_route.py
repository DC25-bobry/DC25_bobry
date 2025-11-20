from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from backend.src.services.synonym_recognition import SynonymRecognizer

router = APIRouter()

class SearchData(BaseModel):
    document: str
    words: List[str]
    threshold: Optional[float] = None

class WordSynonyms(BaseModel):
    word: str
    synonyms: List[str]

class SearchResponse(BaseModel):
    words_synonyms: List[WordSynonyms]

@router.post('/search_synonyms', response_model=SearchResponse)
def find_synonyms(data: SearchData):

    if data.threshold:
        recognizer = SynonymRecognizer(data.document, data.threshold)
    else:
        recognizer = SynonymRecognizer(data.document)

    all_synonyms = []

    for word in data.words:
        current_word_synonyms = WordSynonyms(word=word, synonyms=recognizer.find_synonyms(word))
        all_synonyms.append(current_word_synonyms)

    return SearchResponse(words_synonyms=all_synonyms)
