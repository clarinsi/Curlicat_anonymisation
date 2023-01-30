def get_token_spans(text, tokens):
    pos = 0
    
    d = []
    for token in tokens:
        pos = text.find(token['text'], pos)
        assert pos != -1
        token['start'], token['end'] = pos, pos + len(token['text'])
        d.append(token)
    return d

def ner_tokens_inds(tokens):
    return [i for i, x in enumerate(tokens) if x['ner'] != 'O']

def replace(sentence, token_ids, tokenizer, replacer):
    tokens = tokenizer(sentence)
    
    curr_sentence = sentence
    for i in token_ids:
        curr_tokens = tokenizer(curr_sentence)
        curr_tokens = get_token_spans(curr_sentence, curr_tokens)
        
        start = curr_tokens[i]['start']
        end = curr_tokens[i]['end']
        masked_sentence = curr_sentence[:start] + replacer.tokenizer.mask_token + curr_sentence[end:]
        
        sequences = replacer(masked_sentence)
        # random.shuffle(sequences)
        
        for sequence in sequences:
            cand_tokens = tokenizer(sequence['sequence'])

            # 1. number of tokens should be equal
            if len(cand_tokens) != len(curr_tokens):
                continue
            # 2. NER tags should be equal
            if [x['ner'] for x in curr_tokens] != [x['ner'] for x in cand_tokens]:
                continue
            # 3. tokens should not be equal
            if curr_tokens[i]['text'] == cand_tokens[i]['text']:
                continue
        
            # make replacement
            curr_sentence = sequence['sequence']
            break
            
    return curr_sentence
