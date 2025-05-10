#ABSA module
# Keyword Matching (Simple, Rule-Based)
# Tools: This can be done using Python’s built-in string matching methods or regular expressions.

import logging
logger = logging.getLogger(__name__)

################################################

def extract_sentences_for_aspect_keyword(aspect, text):
    """
    Extract sentences containing the given aspect using keyword matching.
    """
    if not text or not isinstance(text, str):  # Check if text is valid and a string
        raise ValueError("The provided text is invalid or not a string.")
    
    sentences = text.split('.')  # Split the text into sentences (basic approach)
    aspect_sentences = []

    for sentence in sentences:
        if aspect.lower() in sentence.lower():  # Check if aspect is in the sentence
            aspect_sentences.append(sentence.strip())  # Collect matching sentences
    
    return aspect_sentences




# Named Entity Recognition (NER):
# Tools: spaCy (pre-trained NER models) or transformer models like BERT can be used to identify relevant entities

################################################

import spacy

def extract_sentences_for_aspect_NER_Spacy(aspect, text):
    nlp = spacy.load("en_core_web_sm")  # Load spaCy model
    aspect_sentences = []
    doc = nlp(text)
    
    # Check each sentence in the text
    for sent in doc.sents:
        if aspect.lower() in sent.text.lower():
            aspect_sentences.append(sent.text.strip())
    
    return aspect_sentences




# Dependency Parsing:
# Tools: spaCy or BERT can be used for dependency parsing to analyze the syntactic structure of the sentence
# Example with spaCy (dependency parsing):

################################################

import spacy

def extract_sentences_for_aspect_dependench_Spacy(aspect, text):
    nlp = spacy.load("en_core_web_sm")
    aspect_sentences = []
    doc = nlp(text)
    
    # Find sentences containing the aspect and analyze their dependencies
    for sent in doc.sents:
        for token in sent:
            if aspect.lower() in token.text.lower():
                aspect_sentences.append(sent.text.strip())
                break  # Stop after the first match in the sentence
    
    return aspect_sentences


# Contextual Models (e.g., BERT, RoBERTa):
# TExample using Hugging Face Transformers:

################################################

from transformers import pipeline

# Load the model once when the module is imported
nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def extract_sentences_for_aspect_dependency_Transformer(aspect, text):
    if not aspect or not text:
        logger.warning("🚫 Empty aspect or text passed to aspect extraction.")
        return []
    if isinstance(text, list):
        text = " ".join(text)
    # Split into sentences
    sentences = text.split(".")  # or use nltk.sent_tokenize or Spacy

    # Filter valid ones only
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        logging.warning("🚫 No valid sentences to classify.")
        return []

    extracted = []
    for sentence in sentences:
        try:
            result = nlp(sentence, candidate_labels=[aspect])
            if result['scores'][0] > 0.5:  # or your threshold
                extracted.append(sentence)
        except Exception as e:
            logging.error(f"❌ Error processing sentence: '{sentence}' — {e}")
            continue

    return extracted


################################################

def extract_sentences_for_aspect_dependency_Transformer_0(aspect, text):
    if isinstance(text, list):
        text = " ".join(text)

    if not aspect or not text:
        logging.warning("🚫 Empty aspect or text passed to aspect extraction.")
        return []

    sentences = text.split(".")  # or use a better sentence tokenizer
    ...


################################################

import re

def extract_sentences_with_timestamps(aspect, text):
    pattern = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})\s*:\s*(.*)$")
    lines = text.strip().splitlines()
    results = []

    for line in lines:
        match = pattern.match(line)
        if match:
            timestamp, sentence = match.groups()
            result = nlp(sentence, candidate_labels=[aspect])
            if result['labels'][0] == aspect:
                results.append((timestamp.strip(), sentence.strip()))
    return results



