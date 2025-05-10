# file_handling
 
   # Handles uploaded file from form.file_upload:
    #- Saves file
    #- Determines file extension
    #- Extracts text
    #- Returns: dict with filename, path, extension, and text
    
# how to use it:
"""
file_info = handle_uploaded_file(form)

if not file_info or not file_info["file_text"]:
    return jsonify({"error": "Invalid or unsupported file."})

# Access like:
file_text = file_info["file_text"]
filename = file_info["filename"]
file_path = file_info["file_path"]
"""
import os
import re
import pdfplumber
import pandas as pd
from nltk.tokenize import sent_tokenize

# For sentiment analysis
from transformers import AutoTokenizer
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory, current_app


import time

import logging
logger = logging.getLogger(__name__)

def handle_uploaded_file(form, upload_folder):
    uploaded_file = form.file_upload.data
    if not uploaded_file or not hasattr(uploaded_file, 'filename'):
        logger.warning("No uploaded file or missing filename attribute.")
        return None

    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
     # ✅ Ensure the upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    uploaded_file.save(file_path)
    logger.info(f"Saved uploaded file: {file_path}")

    try:
        file_text = extract_text_from_file(file_path)
        logger.info(f"Extracted text length: {len(file_text)}")
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return None

    if not file_text.strip():
        logger.warning("Extracted text is empty after stripping whitespace.")
        return None

    return {
        "filename": filename,
        "file_path": file_path,
        "file_text": file_text
    }


#########################################



sentiment_tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
#chunks = chunk_sentences(clean_text, tokenizer=sentiment_tokenizer)

# For emotion detection
emotion_tokenizer = AutoTokenizer.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")
#chunks = chunk_sentences(clean_text, tokenizer=emotion_tokenizer)


# 1. Extract text from various file types
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    elif ext == '.csv':
        df = pd.read_csv(file_path, on_bad_lines='skip')
        return " ".join(df.astype(str).stack().tolist())

    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

###############################################

    
# 2. Extract clean text from PDF using pdfplumber
def extract_text_from_pdf(file_path):
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text

# 3. Clean extracted text to fix line breaks
def clean_extracted_text(text):
    if isinstance(text, list):
        text = " ".join(text)

    # Now it's safe to apply regex
    text = re.sub(r'\n{2,}', '[PARAGRAPH]', text)
    text = re.sub(r'\s+', ' ', text)  # Normalize spacing
    return text.strip()



# 4. Smart chunking: prioritize paragraphs, fallback to sentence chunks
def smart_chunking(text):
    if "\n\n" in text:
        return split_into_paragraphs(text)
    else:
        return chunk_sentences(text)
###############################################
    
# 5. Paragraph splitter
def split_into_paragraphs(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

# 6. Sentence chunker (e.g., 10 sentences per chunk)
from nltk.tokenize import sent_tokenize

from nltk.tokenize import sent_tokenize

###############################################
# 6. 
def chunk_sentences(text, tokenizer, sentences_per_chunk=10, max_tokens=512):
    sentences = sent_tokenize(text)
    chunks = []
    i = 0

    while i < len(sentences):
        chunk_created = False

        # Try decreasing chunk sizes
        for chunk_size in [sentences_per_chunk, 5, 3, 1]:
            candidate_chunk = sentences[i:i + chunk_size]
            joined = ' '.join(candidate_chunk)
            token_count = len(tokenizer.encode(joined, truncation=False))

            if token_count <= max_tokens:
                chunks.append(joined)
                i += chunk_size
                chunk_created = True
                break  # Successfully chunked

        if not chunk_created:
            # Handle a single sentence longer than token limit
            long_sentence = sentences[i]
            words = long_sentence.split()
            current = ""
            for word in words:
                temp = (current + ' ' + word).strip()
                if len(tokenizer.encode(temp, truncation=False)) > max_tokens:
                    if current:
                        chunks.append(current.strip())
                    current = word
                else:
                    current = temp
            if current:
                chunks.append(current.strip())
            i += 1  # Move to next sentence

    return chunks


#########################################

def get_chunks_from_file(form, tokenizer, upload_folder):
    file_data = handle_uploaded_file(form, upload_folder)
    if not file_data:
        return []

    raw_text = file_data["file_text"]
    logger.info(f"\n\n\n\n1: Raw text before chunking:\n{raw_text}...\n")

    clean_text = clean_extracted_text(raw_text)
    logger.info(f"\n\n\n\n2: Clean text before chunking:\n{clean_text}...\n\n\n")
    
    chunks = chunk_sentences(clean_text, tokenizer=tokenizer)
    return chunks


#########################################
def get__chunk_from_large_text(form, tokenizer):
    
    raw_text = form.large_text.data
    logger.info(f"\n\n\n\n1: Raw text before chunking:\n{raw_text}...\n")

    clean_text = clean_extracted_text(raw_text)
    logger.info(f"\n\n\n\n2: Clean text before chunking:\n{clean_text}...\n\n\n")
    
    chunks = chunk_sentences(clean_text, tokenizer=tokenizer)
    return chunks


#########################################

def get_chunks_from_article(text, tokenizer):
    clean_text = clean_extracted_text(text)
    return chunk_sentences(clean_text, tokenizer=tokenizer)
#########################################


