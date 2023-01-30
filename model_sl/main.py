from fastapi import FastAPI
from pydantic import BaseModel

from anonymize import run

class Prompt(BaseModel):
    text: str

app = FastAPI(docs_url=None, redoc_url=None)

@app.post("/anonymize")
def chat(prompt: Prompt):
    anonymized_text, annotations = run(prompt.text)
    return {
        'original_text': prompt.text,
        'anonymized_text': anonymized_text,
        'annotations': annotations
    }