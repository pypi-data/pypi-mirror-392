# ner_simple

A minimal package that exposes a single function `run_ner(text, model=...)` to run Named Entity Recognition using Hugging Face transformers pipeline.

## Files
- `ner_simple/ner.py` - contains `run_ner` function.
- `requirements.txt` - basic dependencies.

## Usage
```bash
pip install -r requirements.txt
# or install transformers and torch manually
```

```python
from ner_simple import run_ner

text = "Barack Obama was born in Hawaii and was the 44th President of the United States."
entities = run_ner(text)
print(entities)
```

The default model is `dbmdz/bert-large-cased-finetuned-conll03-english` which is fine-tuned for CoNLL-03 NER tasks.