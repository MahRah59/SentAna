

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


import logging
logger = logging.getLogger(__name__)
logger.info("Something happened")


# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")
model = AutoModelForSequenceClassification.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")


# Define the list of real emotion names in the order of the model's logits
EMOTION_CLASSES = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", 
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]



# Define emotion groups (these can be expanded based on the actual emotion classes in your model)
positive_emotions = ['joy', 'excitement', 'love','admiration', 'gratitude','desire','optimism','pride', 'amusement', 'caring','relief', 'approval']
neutral_emotions = ['neutral', 'realization','surprise', 'curiosity']
negative_emotions = ['anger', 'sadness', 'fear', 'nervousness','embarrassment','grief','disappointment','disapproval', 'disgust', 'annoyance', 'confusion', 'remorse']


########################################

#categorize_emotions

def Predict_P_N_N_emotion_scores(comments):

    results = []
    catagorized_emotion_scores = []

    for comment in comments:
        # Tokenize and process the input
        inputs = tokenizer(comment, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # Apply softmax to get probabilities
        scores = torch.softmax(outputs.logits, dim=1).detach().cpu().numpy()[0]

        # Get emotion scores
        emotion_scores = {EMOTION_CLASSES[i]: round(float(score), 2) for i, score in enumerate(scores)}  # Convert to float
         # Initialize sums for the three categories
    positive_score = sum(value for key, value in emotion_scores.items() if key in positive_emotions)
    neutral_score = sum(value for key, value in emotion_scores.items() if key in neutral_emotions)
    negative_score = sum(value for key, value in emotion_scores.items() if key in negative_emotions)


    # Set escalation flag based on the negative emotion score
    escalation_flag = "high" if negative_score > 0.5 else "low"

    results.append({
            "positive_score": positive_score,
            "neutral_score": neutral_score,
            "negative_score": negative_score,
            "escalation_flag": escalation_flag,
            "emotion_scores": emotion_scores
        })
    
    return results

########################################

def Trend_Predict_P_N_N_emotion_scores(comments):

    # Load tokenizer and model

    tokenizer = AutoTokenizer.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")
    model = AutoModelForSequenceClassification.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")


# Define the list of real emotion names in the order of the model's logits
    EMOTION_CLASSES = [
        "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", 
        "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
        "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
        "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
    ]



    # Define emotion groups (these can be expanded based on the actual emotion classes in your model)
    positive_emotions = ['joy', 'excitement', 'love','admiration', 'gratitude','desire','optimism','pride', 'amusement', 'caring','relief', 'approval']
    neutral_emotions = ['neutral', 'realization','surprise', 'curiosity']
    negative_emotions = ['anger', 'sadness', 'fear', 'nervousness','embarrassment','grief','disappointment','disapproval', 'disgust', 'annoyance', 'confusion', 'remorse']  

    results = []
    catagorized_emotion_scores = []

    for comment in comments:
        # Tokenize and process the input
        inputs = tokenizer(comment, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # Apply softmax to get probabilities
        scores = torch.softmax(outputs.logits, dim=1).detach().cpu().numpy()[0]

        # Get emotion scores
        emotion_scores = {EMOTION_CLASSES[i]: round(float(score), 2) for i, score in enumerate(scores)}  # Convert to float
         # Initialize sums for the three categories
    positive_score = sum(value for key, value in emotion_scores.items() if key in positive_emotions)
    neutral_score = sum(value for key, value in emotion_scores.items() if key in neutral_emotions)
    negative_score = sum(value for key, value in emotion_scores.items() if key in negative_emotions)
    print("this is simply positive score",positive_score)


    # Set escalation flag based on the negative emotion score
    escalation_flag = "high" if negative_score > 0.5 else "low"

    results.append({
            "positive_score": positive_score,
            "neutral_score": neutral_score,
            "negative_score": negative_score,
            "escalation_flag": escalation_flag,
            "emotion_scores": emotion_scores
        })
    return results


########################################

def predict_emotions_working(comments):
    """
    Use the GoEmotions model to predict emotions for a list of comments.
    Returns a list of dictionaries containing the emotion scores for each comment.
    """
    results = []
    for comment in comments:
        # Tokenize and process the input
        inputs = tokenizer(comment, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # Apply softmax to get probabilities
        scores = torch.softmax(outputs.logits, dim=1).detach().cpu().numpy()[0]

        # Get emotion scores
        emotion_scores = {
            EMOTION_CLASSES[i]: float(round(score, 2))  # ✅ convert here
            for i, score in enumerate(scores)
        }
        results.append({
            "comment": comment,
            "emotions": emotion_scores
        })
    return results


def predict_emotions(comments):
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    all_scores = torch.softmax(outputs.logits, dim=1).detach().cpu().numpy()

    results = []
    for comment, scores in zip(comments, all_scores):
        emotion_scores = {
            EMOTION_CLASSES[i]: float(round(score, 2))
            for i, score in enumerate(scores)
        }
        results.append({
            "comment": comment,
            "emotions": emotion_scores
        })
    return results

########################################


def generate_mock_emotion_data2(comments):
    """Process input data for emotion detection."""
        # Fetch user input from the form
    raw_comments = request.form.getlist('comments')  # Assume 'comments' contains a list of texts

        # If comments come as a single string, split into a list
    if len(raw_comments) == 1 and isinstance(raw_comments[0], str):
        raw_comments = raw_comments[0].split("@")  # Split by comma and space for individual comments


        # Pass comments to the emotion detection model
    emotion_results = predict_emotions(raw_comments)

        # Map each comment to its predicted emotions
    formatted_results = {
        "comments": raw_comments,  # List of comments
        "emotions": {
            model.config.id2label[i]: round(sum(result[i] for result in emotion_results) / len(emotion_results), 2)
            for i in range(len(model.config.id2label))
            },
        }
    return formatted_results


def generate_mock_emotion_data1(text):
    """Process input data for emotion detection."""
        # Fetch user input from the form
    raw_comments = text

        # If comments come as a single string, split into a list
    if len(raw_comments) == 1 and isinstance(raw_comments[0], str):
        raw_comments = raw_comments[0].split("@")  # Split by comma and space for individual comments


        # Pass comments to the emotion detection model
    emotion_results = predict_emotions1(raw_comments)

        # Map each comment to its predicted emotions
    formatted_results = {
        "comments": raw_comments,  # List of comments
        "emotions": {
            model.config.id2label[i]: round(sum(result[i] for result in emotion_results) / len(emotion_results), 2)
            for i in range(len(model.config.id2label))
            },
        }
    return formatted_results

########################################

def predict_emotions1(texts):
    #Predict emotions for a list of texts.
    # Tokenize input text
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    
    # Predict using the model
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Convert logits to probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return probabilities.numpy()

########################################
import os
import pandas as pd
from PyPDF2 import PdfReader

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    elif ext == '.csv':
        df = pd.read_csv(file_path, on_bad_lines='skip')
        return " ".join(df.astype(str).stack().tolist())

    elif ext == '.pdf':
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

    else:
        raise ValueError(f"Unsupported file type: {ext}")

########################################
    
