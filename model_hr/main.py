from fastapi import FastAPI
from pydantic import BaseModel

from anonymize import replace

#
# HR models
#
import classla
from transformers import pipeline

classla.download(lang='hr')
nlp = classla.Pipeline('hr')

def classla_tokenize(sent):
    return nlp(sent).to_dict()[0][0]

def sentence_split(text):
    sentences = []
    for sent in nlp(text).to_dict():
        sent_text = sent[-1]
        sent_text = sent_text[sent_text.find('# text = ') + len('# text = '):].strip()
        sentences.append(sent_text)
    return sentences

def ner_tokens_inds(tokens):
    return [i for i, x in enumerate(tokens) if x['ner'] != 'O']

tokenizer = classla_tokenize
replacer = pipeline('fill-mask', model='Andrija/SRoBERTa-XL', top_k=40)


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