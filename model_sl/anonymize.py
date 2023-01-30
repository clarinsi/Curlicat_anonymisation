import random

import pandas as pd
import torch
from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          pipeline)

tokenizer = AutoTokenizer.from_pretrained("./models/bert-anon-v1", use_fast=False)
model = AutoModelForTokenClassification.from_pretrained("./models/bert-anon-v1")
nlp_fill = pipeline('fill-mask', model='EMBEDDIA/sloberta', top_k=20)

WINDOW_SIZE = 400
OFFSET = 20
STOPWORDS = [".", ",", ":", ";", "-"]


def get_token_spans(tokens, text):
    pos = 0
    span = []
    for i, token in enumerate(tokens):
        if token.startswith('##'):
            token_text = token[2:]
        else:
            token_text = token
                
        if token == '[UNK]':
            span.append((token, pos, pos))
        else:
            npos = text.find(token_text, pos)
            assert npos != -1
            span.append((token, npos, npos + len(token_text)))
            pos = npos + len(token_text)
    return span


def group_spans(spans, preds):
    res = []
    for (word, s, e), p in zip(spans, preds):
        if word.startswith('##'):
            res[-1][0] += word[2:]
            res[-1][2] = e
            res[-1][3] = max(res[-1][3], p)
        else:
            res.append([word, s, e, p])
    return res


def simple_replacer(w):
    if w.isdigit():
        return "".join([str(random.randint(0,9)) 
                        for x in range(len(w))])
    elif w in [".", ",", ":", ";", "-"]:
        return w    
    elif w in ['si', 'com', 'net']:
        return w
    return float('nan')
    

def run(text):
    tokens = tokenizer.tokenize(text)

    logits = []
    for i in range(0, len(tokens), WINDOW_SIZE):
        start, end = max(0, i - OFFSET), i + WINDOW_SIZE
        ignore_first = end - start - WINDOW_SIZE
        input_ids = torch.tensor([(tokenizer.convert_tokens_to_ids(
                    ['[CLS]'] + tokens[start:end] + ['[SEP]']))])
        logits.append(model(input_ids).logits[0, 1 + ignore_first:-1])
    logits = torch.concat(logits)

    pred = torch.argmax(logits, dim=-1)

    spans = get_token_spans(tokens, text)
    spans = group_spans(spans, pred.tolist())

    sf = pd.DataFrame(spans)
    sf.columns = ['content', 'start', 'end', 'mask']
    sf['mask'] = sf['mask'].apply(bool)
    sf = sf[sf['mask']]

    sf = sf[~sf['content'].isin(STOPWORDS)]
    sf['replace_with'] = sf['content'].apply(simple_replacer)
    sub = sf[sf['replace_with'].isna()].copy()

    sents = []
    for s, e in zip(sub.start, sub.end):
        sent_mask = list(text)
        sent_mask[s:e] = list(nlp_fill.tokenizer.mask_token)
        sent_mask = ''.join(sent_mask)
        sents.append(sent_mask)
    sub['sent_mask'] = sents

    # Perform replacement
    sub['repl'] = sub['sent_mask'].apply(nlp_fill)
    sub['repl'] = sub['repl'].apply(lambda x: x[0]['token_str'])

    sf.loc[sf['replace_with'].isna(), 'replace_with'] = sub['repl']
    
    new_text = ""
    p = 0
    for _, row in sf.iterrows():
        new_text += text[p:row.start]
        new_text += row['replace_with']
        p = row.end
    new_text += text[p:]

    return new_text, sf[['content', 'start', 'end', 'replace_with']].to_dict(orient='records')
    