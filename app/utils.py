import re
import requests
import tweepy
from tweepy import TweepyException  # Use the new exception classfrom dotenv import load_dotenv
import os
from dotenv import load_dotenv

DEEPL_API_KEY = "0bd1b7a9-d82c-445b-8209-1897589e990f:fx"


# Load environment variables from .env file
load_dotenv()

########################################

def setup_twitter_api():
    """
    Set up the Twitter API client using credentials from environment variables.
    """
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
    
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

########################################

def fetch_social_media_text(social_input):
    
   # Fetches text data from social media input like Twitter URLs or handles. Example for Twitter only. Extendable for other platforms. Fetch tweets for a given Twitter handle or URL.
   # Args:
       # input_text (str): Twitter handle (e.g., '@elonmusk') or URL (e.g., 'https://twitter.com/elonmusk').
    #Returns:
        #str: Combined text of recent tweets or None if an error occurs.
    
    api = setup_twitter_api()  # Set up the Twitter API client
    print(api.get_user(id="self").screen_name)  # Should return your Twitter username

    print("begining of fetch_social_media_text")

    if 'twitter.com' in social_input:
        # Extract the handle or tweet ID from the URL
        match = re.search(r'twitter\.com\/([^\/]+)', social_input)
        if match:
            handle = match.group(1)  # Extract Twitter handle

            # Fetch the latest tweets from the handle
            tweet_texts = fetch_twitter_text(handle)
            return tweet_texts
            print(tweet_texts)
            print("end of fetch_social_media_text")

        else:
            return "Invalid Twitter URL or format."

    # Placeholder for other platforms
    return "Social media platform not yet supported."

########################################


def fetch_twitter_text(handle):
    
    #Fetch the latest tweets from a given Twitter handle using the Twitter API.
    
    try:
        #api = setup_twitter_api()  # Setup API internally
        tweets = api.user_timeline(screen_name=handle, count=10, tweet_mode="extended")
        tweet_texts = [tweet.full_text for tweet in tweets]
        return " ".join(tweet_texts)  # Combine all tweets into one text block
    except TweepyException as e:
        #return f"Error fetching tweets: {str(e)}"
        print(f"Error fetching tweets for {handle}: {str(e)}")
        return None  # Return None for errors

def get_tweet_text(tweet_id):
    
    #Fetch tweet text by tweet ID using the Twitter API.
    
    try:
        api = setup_twitter_api()  # Setup API internally
        tweet = api.get_status(tweet_id, tweet_mode="extended")
        return tweet.full_text
    except TweepyException as e:
        return f"Error fetching tweet: {str(e)}"


def perform_basic_analysis(platform, input_type, input_value):
    # Basic analysis logic here
    return {"platform": platform, "input_type": input_type, "input_value": input_value, "sentiment": "Positive"}

def perform_advanced_analysis(analysis_type, text):
    if analysis_type == 'emotion':
        return detect_emotions(text)
    elif analysis_type == 'intent':
        return classify_intent(text)

def detect_emotions(text):
    # Logic for emotion detection (e.g., using GoEmotions dataset)
    return {"text": text, "emotions": {"joy": 0.6, "sadness": 0.2, "anger": 0.2}}

def classify_intent(text):
    # Logic for intent classification (e.g., purchase intent, complaint)
    return {"text": text, "intent": "Purchase Intent"}

########################################

import json

def process_input_data(form):
    input_data = []

    if form.input_type.data == 'text':  # Text input field
        input_data = [form.text_input.data.strip()]
    
    elif form.input_type.data == 'file':  # File upload
        file = form.file_upload.data
        if file:
            input_data = [line.strip() for line in file.read().decode('utf-8').splitlines()]
    
    elif form.input_type.data in ['twitter', 'facebook', 'youtube']:  # Social media
        social_media_handler = {
            'twitter': fetch_twitter_data,
            'facebook': fetch_facebook_data,
            'youtube': fetch_youtube_data,
        }
        input_data = social_media_handler[form.input_type.data](form.social_media_input.data)
    
    elif form.input_type.data == 'mock':  # Mock data
        input_data = generate_mock_data()
    
    # Preprocessing (e.g., cleaning, batching)
    input_data = [clean_text(text) for text in input_data]

    # Return structured data
    return {"input_type": form.input_type.data, "data": input_data}

########################################

import re
from datetime import datetime
import pytz

def extract_timestamp_from_text(text):
    """
    Extract the timestamp from the text. This example assumes the timestamp
    is in a specific format like 'Tue Apr 21 01:04:03 PDT 2009'.
    Modify the regex pattern and datetime parsing to match your format.
    """
    timestamp_pattern = r"\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \w{3} \d{4}"
    match = re.search(timestamp_pattern, text)
    
    if match:
        timestamp_str = match.group(0)
        try:
            timestamp = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Z %Y")
            return timestamp
        except ValueError:
            print(f"Error parsing timestamp: {timestamp_str}")
            return None
    return None



########################################
# Option 1 : if langdetect is used:
# this function is defined also in route.py 

from langdetect import detect, LangDetectException

def detect_language(text):
    if not text or not text.strip():
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


########################################
# Option 2 : if fasttext is used:
# this function is defined also in route.py 


import fasttext
import os

# Define the model path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/lid.176.bin")
#MODEL_PATH= "/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/app/models"

# Load model
try:
    model = fasttext.load_model(MODEL_PATH)
except Exception as e:
    print(f"Error loading FastText model: {e}")
    model = None  # Fallback in case of failure

def detect_language(text):
    if not text:
        return "unknown"  # ✅ Prevent crash on None or empty string

    if model is None:
        return "unknown"

    text = text.replace("\n", " ")  # Safe now because text is not None
    predictions = model.predict(text, k=1)
    return predictions[0][0].replace("__label__", "")



########################################


import re

# Define slang dictionary globally (outside the function)
slang_dict = {
    "gonna": "going to",
    "wanna": "want to",
    "lemme": "let me",
    "ain't": "is not",
    "brb": "be right back",
    "btw": "by the way",
    "lmao": "laughing out loud",
    "omg": "oh my god",
    "idk": "I don't know",
    "smh": "shaking my head",
    "tbh": "to be honest",
    "y'all": "you all",
    "thx": "thanks",
    "cuz": "because",
    "ur": "your",
    "plz": "please",
    "tho": "though",
    "af": "as heck",
    "jk": "just kidding",
    "ttyl": "talk to you later",
    "gtg": "got to go",
    "rofl": "rolling on the floor laughing",
    "fomo": "fear of missing out",
    "hmu": "hit me up",
    "dm": "direct message",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "sync up": "meet to discuss",
    "touch base": "follow up",
    "circle back": "revisit later",
    "low-hanging fruit": "easy task",
    "deep dive": "detailed analysis",
    "think outside the box": "be creative",
    "bandwidth": "availability",
    "leverage": "use",
    "onboarding": "employee training",
    "bug": "software issue",
    "patch": "software update",
    "deploy": "release",
    "stack": "technology set",
    "devs": "developers",
    "repo": "repository",
    "pull request": "code submission",
    "hotfix": "urgent bug fix",
    "nerf": "reduce effectiveness",
    "buff": "increase effectiveness",
    "gg": "good game",
    "op": "overpowered",
    "meta": "most effective tactic available",
    "noob": "beginner",
    "afk": "away from keyboard",
    "rekt": "completely defeated",
    "smurf": "experienced player using a new account",
    "stat": "immediately",
    "script": "prescription",
    "dx": "diagnosis",
    "rx": "medication",
    "ed": "emergency department",
    "otc": "over-the-counter",
    "vax": "vaccine",
    "bullish": "expecting price to rise",
    "bearish": "expecting price to drop",
    "hodl": "hold on to investment",
    "pump and dump": "inflated stock followed by sell-off",
    "bagholder": "investor stuck with worthless stock",
    "moon": "rapid price increase",
}

def replace_slang(text, raw_text=False):
    """
    Replace slang words in the text unless raw_text=True.
    """
    if raw_text:  # If raw_text is True, return text as it is
        return text

    def slang_replacer(match):
        word = match.group(0).lower()
        return slang_dict.get(word, word)  # Replace if found, else return original word

    # Replace whole words while ignoring case
    pattern = r'\b(' + '|'.join(re.escape(word) for word in slang_dict.keys()) + r')\b'
    return re.sub(pattern, slang_replacer, text, flags=re.IGNORECASE)



########################################
# pip install googletrans==4.0.0-rc1
#old translate_to_english
"""
import logging
from googletrans import Translator
import difflib

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
translator = Translator()


def translate_to_english(text, detected_lang):
    if detected_lang == "en":
        return text  # No translation needed

    # Replace slang before translation
    text = replace_slang(text)

    try:
        translated_text = translator.translate(text, src=detected_lang, dest="en").text

        # Check similarity between original and translated text
        similarity = difflib.SequenceMatcher(None, text, translated_text).ratio()

        if similarity < 0.3:  
            logging.warning(f"⚠️ Low similarity ({similarity}) between original and translated text. Using original text instead.")
            return text  # Return original instead of unreliable translation

        return translated_text

    except Exception as e:
        logging.warning(f"⚠️ Translation failed for language '{detected_lang}': {e}")
        return text  # Fallback to original text

"""
########################################


import logging
import deepl  # ✅ Using DeepL instead of googletrans

# Replace with your actual DeepL API key
translator = deepl.Translator(DEEPL_API_KEY)

def translate_to_english(text, detected_lang):
    if detected_lang == "en":
        return text  # No translation needed

    # Replace slang before translation
    text = replace_slang(text)

    try:
        return translator.translate_text(text, source_lang=detected_lang.upper(), target_lang="EN-US").text

    except Exception as e:
        logging.warning(f"⚠️ DeepL Translation failed for language '{detected_lang}': {e}")
        return text  # Fallback to original text


########################################
    
    
########################################