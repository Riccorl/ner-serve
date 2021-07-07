from typing import List

from pydantic import BaseModel


class WordOut(BaseModel):
    index: int
    text: str
    ner_tag: str


class DocumentOut(BaseModel):
    tokens: List[WordOut] = []
