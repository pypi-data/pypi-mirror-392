"""
ner_simple

Provides a lightweight helper to run NER using Hugging Face transformers pipeline.
"""
from .ner import run_ner

__all__ = ["run_ner"]