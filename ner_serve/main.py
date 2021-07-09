from fastapi import FastAPI
from objects import DocumentOut

from model import NerModel

app = FastAPI(title="Simple NER Model", version="1.0.0")
model = NerModel()


@app.get("/api/ner", response_model=DocumentOut)
def predict(sentence: str):
    return model([sentence])[0]
