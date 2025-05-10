# sentiment_analysis.py

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

from .forms import SentimentAnalysisForm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect
from .utils import detect_language, translate_to_english, replace_slang

# from .utils import detect_language_lngdetect # if detectlang is used

import logging
logger = logging.getLogger(__name__)

from transformers import AutoTokenizer, AutoModelForSequenceClassification

#tokenizer = AutoTokenizer.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")
#model = AutoModelForSequenceClassification.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")



###########################################

# Transformer-based sentiment analysis
def analyze_transformer_sentiment(text, raw_text=False):
    lang = detect_language(text)

    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    supported_languages = get_supported_languages(model_name)

    if lang == "en":
        text = replace_slang(text, raw_text)  # Only refine slang
    elif lang not in supported_languages:  
        text = translate_to_english(text, lang)
        if not text:
            return {"error": f"Failed to translate language '{lang}'"}

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1).squeeze().tolist()

    labels = ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
    predicted_index = torch.argmax(torch.tensor(probs)).item()
    predicted_label = labels[predicted_index]
    predicted_score = probs[predicted_index]

    return {
        "all_scores": {label: prob for label, prob in zip(labels, probs)},
        "predicted_label": predicted_label,
        "predicted_score": predicted_score,
    }

###########################################

def analyze_Mock_sentiment(text):
    # Example using VADER or your Transformer model
    if len(text) < 200:
        analyzer = SentimentIntensityAnalyzer()
        return analyzer.polarity_scores(text)
    else:
        # Transformer model for larger texts
        return analyze_transformer_sentiment(text)

###########################################

def analyze_vader_sentiment(text, display_option=None, raw_text=False):
    lang = detect_language(text)

    if lang == "en":
        text = replace_slang(text, raw_text)  # Apply slang correction unless raw_text=True
    else:
        text = translate_to_english(text, lang)
        if not text:
            return {"error": f"Failed to translate language '{lang}'"}

    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)

    if display_option == "summary":
        return {
            "positive": sentiment_scores["pos"],
            "negative": sentiment_scores["neg"],
            "neutral": sentiment_scores["neu"],
            "overall": sentiment_scores["compound"],
        }
    return sentiment_scores  # Default behavior


###########################################
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect as detect_language

#Not Used !!!!!!!  #Not Used !!!!!!!  
def analyze_transformer_sentiment_chunks_0(chunks):
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    labels = ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
    total_scores = torch.zeros(len(labels))
    num_chunks = 0


    for chunk in chunks:
        lang = detect_language(chunk)
        logger.info(f"The Chunk is --------------: {chunk}")

        if lang == "en":
            chunk = replace_slang(chunk)
        elif lang not in get_supported_languages(model_name):
            chunk = translate_to_english(chunk, lang)
            logger.info(f" \n\n chunk after translation is : {chunk}")
            if not chunk:
                continue  # Skip if translation failed

        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1).squeeze()
        total_scores += probs
        num_chunks += 1

    if num_chunks == 0:
        return {"error": "No valid chunks were analyzed."}

    avg_scores = (total_scores / num_chunks).tolist()
    predicted_index = torch.argmax(torch.tensor(avg_scores)).item()

    return {
        "all_scores": {label: round(score, 4) for label, score in zip(labels, avg_scores)},
        "predicted_label": labels[predicted_index],
        "predicted_score": round(avg_scores[predicted_index], 4),
        "chunks_analyzed": num_chunks
    }
###########################################
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langdetect import detect as detect_language, LangDetectException

def analyze_transformer_sentiment_chunks(chunks):
    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    labels = ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
    total_scores = torch.zeros(len(labels))
    num_chunks = 0

    for chunk in chunks:
        if not chunk.strip():
            continue

        # 🛡️ Detect language safely
        try:
            lang = detect_language(chunk)
        except LangDetectException:
            lang = "unknown"

        logger.info(f"🌐 Detected language: {lang}")
        logger.info(f"🔍 Analyzing chunk: {chunk[:100]}...")

        # 🔁 Slang replacement or translation
        if lang == "en":
            chunk = replace_slang(chunk)
        elif lang not in get_supported_languages(model_name):
            chunk = translate_to_english(chunk, lang)
            logger.info(f" \n\n chunk after translation is : {chunk}")

            if not chunk:
                logger.warning("⚠️ Translation failed or returned empty. Skipping.")
                continue

        try:
            inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)
            logits = model(**inputs).logits
            probs = F.softmax(logits, dim=-1).squeeze()
            total_scores += probs
            num_chunks += 1
        except Exception as e:
            logger.error(f"❌ Sentiment model failed on chunk: {str(e)}")
            continue

    if num_chunks == 0:
        logger.warning("⚠️ No chunks successfully analyzed.")
        return {
            "all_scores": {label: 0.0 for label in labels},
            "predicted_label": "unknown",
            "predicted_score": 0.0,
            "chunks_analyzed": 0
        }

    avg_scores = (total_scores / num_chunks).tolist()
    predicted_index = torch.argmax(torch.tensor(avg_scores)).item()

    return {
        "all_scores": {label: round(score, 4) for label, score in zip(labels, avg_scores)},
        "predicted_label": labels[predicted_index],
        "predicted_score": round(avg_scores[predicted_index], 4),
        "chunks_analyzed": num_chunks
    }

###########################################

from transformers import AutoTokenizer

def get_supported_languages(model_name):
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        return tokenizer.init_kwargs.get("languages", ["en"])  # Default to English if not available
    except Exception:
        return ["en"]  # Fallback to English if model metadata is unavailable


###########################################

import matplotlib.pyplot as plt
import numpy as np

def plot_sentiment_trends(sentiments):
    # sentiments: a list of sentiment scores over time
    time = np.arange(len(sentiments))
    plt.plot(time, sentiments, label="Sentiment over time")
    plt.xlabel('Message number')
    plt.ylabel('Sentiment Score')
    plt.title('Sentiment Trend in Chat')
    plt.show()

###########################################