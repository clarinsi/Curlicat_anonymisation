from fastapi import FastAPI
from pydantic import BaseModel

from anonymize import replace

#
# PL models
#
import spacy
from transformers import pipeline

nlp_spacy = spacy.load("pl_core_news_md")

def spacy_tokenize(sent):
    doc = nlp_spacy(sent)
    return [
        {'text': str(t), 'ner': 'O' if t.ent_type_ == '' else t.ent_type_, 'feats': ''}
        for t in doc
    ]

def sentence_split(text):
    return [str(x) for x in nlp_spacy(text).sents]

def ner_tokens_inds(tokens):
    return [i for i, x in enumerate(tokens) if x['ner'] != 'O']

tokenizer = spacy_tokenize
replacer = pipeline('fill-mask', model='allegro/herbert-base-cased', top_k=40)

#
# API
#

class Prompt(BaseModel):
    text: str
    format: str

app = FastAPI(docs_url=None, redoc_url=None)

@app.post("/anonymize")
def chat(prompt: Prompt):
    text = prompt.text
    sentences = sentence_split(text)
    
    anon_sentences = []
    for sentence in sentences:
        anon_sentences.append(replace(sentence, ner_tokens_inds(tokenizer(sentence)), tokenizer, replacer))
    anon_text = " ".join(anon_sentences)

    return {
        'original_text': prompt.text,
        'anonymized_text': anon_text,
        'format': 'text'
    }