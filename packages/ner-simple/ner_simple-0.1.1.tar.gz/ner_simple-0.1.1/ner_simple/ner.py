from typing import List, Dict, Union
from transformers import pipeline

def run_ner(text: Union[str, List[str]], model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"):

    nlp = pipeline("ner", model=model, aggregation_strategy="simple")
    single = False
    if isinstance(text, str):
        single = True
        texts = [text]
    else:
        texts = text
    outputs = [nlp(t) for t in texts]
    return outputs[0] if single else outputs
