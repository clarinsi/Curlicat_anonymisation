from fastapi import FastAPI, Request
from pydantic import BaseModel

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException


import requests
import json

with open('config.tsv', 'r') as f:
    uris = {}
    for ln in f:
        lang, uri = ln.strip().split(',')
        uris[lang] = uri

with open('description.md', 'r') as f:
    description = f.read()

class Prompt(BaseModel):
    text: str
    lang: str

app = FastAPI(
    title="Curlicat anonymization tool",
    description=description,
    version="0.0.1",
    docs_url='/documentation', redoc_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/anonymize")
def anonymize(prompt: Prompt):
    text = prompt.text
    anon_text = prompt.text

    if prompt.lang not in uris:
        raise HTTPException(status_code=400, detail="Invalid language.")
    else:
        try:
            data = {'text': text, 'format': 'text'}
            r = requests.post(uris[prompt.lang], json=data)
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=r.text)
            else:
                anon_text = json.loads(r.text)['anonymized_text']
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Internal server error.")
    
    return {
        'original_text': text,
        'anonymized_text': anon_text,
        'lang': prompt.lang
    }
