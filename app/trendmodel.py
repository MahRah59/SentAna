import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from .sentiment_analysis import analyze_vader_sentiment, analyze_transformer_sentiment
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import time

import numpy as np

# VADER-based sentiment analysis
#from .forms import VaderForm, TransformerForm, CombinedAnalysisForm
#from .forms import CombinedAnalysisForm
from .forms import SentimentAnalysisForm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#from app.utils import extract_timestamp_from_text  # Or adjust if it's located in another file
from .sentiment_analysis import analyze_transformer_sentiment_chunks


from app.file_handling import handle_uploaded_file, extract_text_from_file, extract_text_from_pdf, clean_extracted_text
from app.file_handling import smart_chunking, split_into_paragraphs, chunk_sentences

import logging
logger = logging.getLogger(__name__)


sentiment_tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
#chunks = chunk_sentences(clean_text, tokenizer=sentiment_tokenizer)

# For emotion detection
emotion_tokenizer = AutoTokenizer.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")
#chunks = chunk_sentences(clean_text, tokenizer=emotion_tokenizer)

########################################


def fetch_messages(start_date, end_date, user_id=None, session_id=None, aspect_based=None):
    conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
    cursor = conn.cursor()
    
    # Building the query dynamically based on parameters passed
    query = 'SELECT * FROM chatMessages WHERE timestamp BETWEEN ? AND ?'
    params = [start_date, end_date]
    
    
    # Adding conditions for user_id, session_id, or aspect_based
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
    if session_id:
        query += ' AND session_id = ?'
        params.append(session_id)
    if aspect_based:
        query += ' AND additional_info LIKE ?'
        params.append(f"%{aspect_based}%")

    cursor.execute(query, params)
    messages = cursor.fetchall()
    #print(f"Fetched messages: {messages}")  # Debugging line
    conn.close()
    return messages




import re
from dateutil import parser
import pytz
import logging

logger = logging.getLogger(__name__)

# === Timezone Map (if needed for future enhancement) ===
timezone_map = {
    "PDT": pytz.timezone("US/Pacific"),
    "GMT": pytz.timezone("GMT"),
    "EST": pytz.timezone("US/Eastern"),
    "CST": pytz.timezone("US/Central"),
    "MST": pytz.timezone("US/Mountain"),
    "UTC": pytz.utc,
}
tzinfos = {tz: timezone_map[tz] for tz in timezone_map}

##################################################

def group_by_time_scale_file(lines, time_scale='monthly'):
    grouped_data = {}

    for line in lines:
        if not isinstance(line, str):
            continue

        # Try to extract timestamp with regex or part index
        timestamp = extract_timestamp_from_text(line)
        if not timestamp:
            continue

        period = format_period(timestamp, time_scale)
        grouped_data.setdefault(period, []).append(line)

    return grouped_data



##################################################

def group_by_time_scale(data, time_scale='monthly'):
    grouped_data = {}

    # Handle large text
    if isinstance(data, str):
        if not validate_large_text_format(data):
            logger.warning("⚠️ Not enough timestamp markers in large text: No vailidated large text.")
            return grouped_data
        segments = data.splitlines()
        logger.info(f" Segments are: {segments}")

    else:
        segments = data  # list of strings or dicts
        logger.info(f" Segments = data is: {segments}")

    for item in segments:
        # If item is a dict (e.g. chat message from DB)
        if isinstance(item, dict) and "timestamp" in item:
            candidate = item["timestamp"]
            content = item.get("text", "")
        elif isinstance(item, str):
            # Parse CSV-style string
            parts = item.split(",")
            candidate = parts[2].strip().strip('"') if len(parts) >= 3 else item
            content = item
        else:
            continue  # Skip unsupported types

        timestamp = extract_timestamp_from_text(candidate)
        if not timestamp:
            logger.info(f" No Timestamp")
            continue
        else:
            logger.info(f"The Timestamp is: {timestamp}")
        # Time scale grouping
        if time_scale == 'monthly':
            period = timestamp.strftime('%Y-%m')
        elif time_scale == 'weekly':
            period = f"{timestamp.year}-W{timestamp.isocalendar()[1]:02d}"
        elif time_scale == 'daily':
            period = timestamp.strftime('%Y-%m-%d')
        elif time_scale == 'quarterly':
            quarter = (timestamp.month - 1) // 3 + 1
            period = f"{timestamp.year}-Q{quarter}"
        elif time_scale == 'yearly':
            period = str(timestamp.year)
        else:
            raise ValueError("Invalid time scale")

        grouped_data.setdefault(period, []).append(content)
        grouped_data.pop('', None)

    return grouped_data


########################################

def group_by_time_scale_chatMessages(messages, time_scale='monthly'):
    grouped_data = {}

    for msg in messages:
        if isinstance(msg, dict) and 'timestamp' in msg:
            timestamp = msg['timestamp']
            content = msg['text']
        elif isinstance(msg, tuple) and len(msg) >= 5:
            timestamp = msg[4]
            content = msg[3]
        else:
            logger.info("⚠️ Skipped: Not a valid dict or tuple with timestamp.")
            continue

        try:
            ts = parse(timestamp)
            period = format_period(ts, time_scale)
            grouped_data.setdefault(period, []).append(content)
        except Exception as e:
            logger.warning(f"❌ Failed to parse timestamp: {e}")

    return grouped_data


########################################

import re
from dateutil.parser import parse

def group_by_time_scale_largeText(text, time_scale='monthly'):
    grouped_data = {}

    if isinstance(text, list):
        text = " ".join(text)  # or text = text[0] if only one item expected
    if not isinstance(text, str):
        logger.warning("Expected string input for largeText.")
        return grouped_data

    if not isinstance(text, str):
        logger.warning("Expected string input for largeText.")
        logger.info(f"Group data will be returned")
        return grouped_data

    pattern = r"(?=\d{4}-\d{2}-\d{2}\s*[\"“”])"
    chunks = re.split(pattern, text)

    for chunk in chunks:
        if not chunk.strip():
            logger.info(f" No Chunck for large tect grouping")
            continue
        logger.info(f" chunk in larg text grouping is: {chunk}")
        match = re.search(r"(\d{4}-\d{2}-\d{2})", chunk)
        if not match:
            continue

        try:
            timestamp = parse(match.group(1))
            if timestamp:
                logger.info(f" Timestamp is {timestamp}")
            else:
                logger.info(f" NO Timestamp")
            period = format_period(timestamp, time_scale)
            grouped_data.setdefault(period, []).append(chunk.strip())
        except Exception as e:
            logger.warning(f"⛔ Failed to parse timestamp: {e}")
            continue

    return grouped_data




########################################

import time
import re

from dateutil.parser import parse

def validate_large_text_format(text):
    import time
    start = time.time()
    
    timestamps = []
    lines = text.splitlines()

    for line in lines:
        try:
            # Try fuzzy parsing each line to find a timestamp
            dt = parse(line, fuzzy=True)
            timestamps.append(dt.date())
        except Exception:
            continue

    unique_dates = set(timestamps)
    result = len(unique_dates) >= 2  # Or 1, if you want to relax this
    print(f"⏱️ validate_large_text_format took {time.time() - start:.2f} sec")
    return result

########################################


def format_period(timestamp, time_scale):
    if time_scale == 'monthly':
        return timestamp.strftime('%Y-%m')
    elif time_scale == 'weekly':
        return f"{timestamp.year}-W{timestamp.isocalendar()[1]:02d}"
    elif time_scale == 'daily':
        return timestamp.strftime('%Y-%m-%d')
    elif time_scale == 'quarterly':
        quarter = (timestamp.month - 1) // 3 + 1
        return f"{timestamp.year}-Q{quarter}"
    elif time_scale == 'yearly':
        return str(timestamp.year)
    else:
        raise ValueError("Invalid time scale")

########################################

import re
from dateutil.parser import parse
from dateutil import parser
import pytz

# Optional timezone info
tzinfos = {
    "PDT": -7 * 3600, "PST": -8 * 3600, "EDT": -4 * 3600,
    "EST": -5 * 3600, "CDT": -5 * 3600, "CST": -6 * 3600,
    "MDT": -6 * 3600, "MST": -7 * 3600, "UTC": 0, "GMT": 0,
}

# Common timestamp patterns
timestamp_patterns = [
    r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}",                    # 2025-04-24 12:30:45
    r"[A-Z][a-z]{2} [A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2} [A-Z]{2,4} \d{4}",  # Tue Apr 07 00:41:44 PDT 2009
    r"\d{2}/\d{2}/\d{4}",                                         # 24/04/2025
    r"\d{4}/\d{2}/\d{2}",                                         # 2025/04/24
    r"\d{2}-\d{2}-\d{4}",                                         # 24-04-2025
]

def extract_timestamp_from_text(text):
    if not isinstance(text, str):
        print(f"⚠️ Skipping non-string input: {text}")
        return None

    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return parse(match.group(), fuzzy=False, tzinfos=tzinfos)
            except Exception as e:
                print(f"❌ Failed to parse '{match.group()}': {e}")
    return None


########################################
########################################
########################################
########################################
#OLD_Section: 

def fetch_messages(start_date, end_date, user_id=None, session_id=None, aspect_based=None):
    conn = sqlite3.connect('/Users/MR_1/MyApplications/TestSentAna_CRM_Integrtion/instance/site.db')
    cursor = conn.cursor()
    
    # Building the query dynamically based on parameters passed
    query = 'SELECT * FROM chatMessages WHERE timestamp BETWEEN ? AND ?'
    params = [start_date, end_date]
    source_type= "DateBase: ChatMessages"
    
    # Adding conditions for user_id, session_id, or aspect_based
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
    if session_id:
        query += ' AND session_id = ?'
        params.append(session_id)
    if aspect_based:
        query += ' AND additional_info LIKE ?'
        params.append(f"%{aspect_based}%")

    cursor.execute(query, params)
    messages = cursor.fetchall()
    #print(f"Fetched messages: {messages}")  # Debugging line
    conn.close()
    return messages, source_type




import re
from dateutil import parser
import pytz
import logging

logger = logging.getLogger(__name__)

# === Timezone Map (if needed for future enhancement) ===
timezone_map = {
    "PDT": pytz.timezone("US/Pacific"),
    "GMT": pytz.timezone("GMT"),
    "EST": pytz.timezone("US/Eastern"),
    "CST": pytz.timezone("US/Central"),
    "MST": pytz.timezone("US/Mountain"),
    "UTC": pytz.utc,
}
tzinfos = {tz: timezone_map[tz] for tz in timezone_map}

def extract_timestamp_from_text_1(text):
    """
    Extract timestamp from various data types:
    - Chat messages with datetime fields
    - Unstructured text sections starting with YYYY-MM-DD
    - Text with embedded timestamp strings

    Returns:
        datetime.datetime or None
    """
    # A) Handle chat message dict with explicit timestamp field
    if isinstance(text, dict) and "timestamp" in text:
        try:
            return parser.parse(text["timestamp"], tzinfos=tzinfos)
        except Exception as e:
            logger.warning(f"Failed to parse timestamp from dict: {e}")
            return None

    # B) Handle structured list/tuple formats (e.g., DB rows)
    if isinstance(text, (list, tuple)) and len(text) > 4:
        try:
            return parser.parse(text[4], tzinfos=tzinfos)
        except Exception as e:
            logger.warning(f"Failed to parse timestamp from tuple/list: {e}")
            return None

    # C) Handle unstructured large text - extract date at the beginning or inline
    if isinstance(text, str):
        match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if match:
            try:
                return parser.parse(match.group(1))
            except Exception as e:
                logger.warning(f"Failed to parse extracted date string: {e}")
                return None

    logger.debug("No valid timestamp found in input.")
    return None

def validate_large_text_format_1(text):
    """
    Quick pre-check to determine if the large text contains valid timestamp markers.
    """
    potential_dates = re.findall(r'(\d{4}-\d{2}-\d{2})', text)
    return len(potential_dates) >= 2  # Require at least 2 timestamps to make grouping meaningful

def group_by_time_scale_1(data, time_scale='monthly'):
    """
    Groups items by extracted timestamps and chosen time scale.

    Args:
        data: str (unstructured text) OR list of items (chat messages, dicts, etc.)
        time_scale: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'

    Returns:
        dict with period -> list of text entries
    """
    grouped_data = {}

    # Handle unstructured large text by splitting on dates
    if isinstance(data, str):
        if not validate_large_text_format_1(data):
            logger.warning("⚠️ Large text does not contain enough timestamp markers. Grouping may be skipped.")
            return grouped_data
        segments = re.split(r'(?=\d{4}-\d{2}-\d{2})', data)
    else:
        segments = data

    for item in segments:
        timestamp = extract_timestamp_from_text(item)

        if not timestamp:
            logger.info(f"⏭️ Skipping segment: No valid timestamp found. Item: {str(item)[:100]}...")
            continue

        if time_scale == 'daily':
            period = timestamp.strftime('%Y-%m-%d')
        elif time_scale == 'weekly':
            period = f"{timestamp.year}-W{timestamp.isocalendar()[1]:02d}"
        elif time_scale == 'monthly':
            period = timestamp.strftime('%Y-%m')
        elif time_scale == 'quarterly':
            quarter = (timestamp.month - 1) // 3 + 1
            period = f"{timestamp.year}-Q{quarter}"
        elif time_scale == 'yearly':
            period = str(timestamp.year)
        else:
            raise ValueError("❌ Invalid time scale provided.")

        grouped_data.setdefault(period, []).append(item)
        logger.debug(f"📅 Grouped item under period {period}")

    return grouped_data





########################################
########################################
########################################
########################################
########################################

"""
from dateutil import parser
import pytz
import re

def extract_timestamp_from_text(line):
    
    #Extracts and formats a timestamp from a single line of text.

    #Args: line (str): A single line of text containing a potential timestamp.

    #Returns: str or None: Formatted timestamp in 'YYYY-MM-DD HH:MM:SS' format, or None if no valid timestamp is found.
    
    # Define timezone mapping for PDT, EST, etc.
    timezone_map = {
        "PDT": pytz.timezone("US/Pacific"),
        "GMT": pytz.timezone("GMT"),
        "EST": pytz.timezone("US/Eastern"),
        "CST": pytz.timezone("US/Central"),
        "MST": pytz.timezone("US/Mountain"),
        "UTC": pytz.utc,
    }

    tzinfos = {tz: timezone_map[tz] for tz in timezone_map}

    # Define regex pattern for timestamps
    timestamp_regex = r"\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+(\w+)\s+\d{4}"

    # Find matches in the line
    match = re.search(timestamp_regex, line)

    if not match:
        
        print(f"Skipping line: No valid timestamp found. Line: {line}")
        logger.info(f"Skipping line: No valid timestamp found. Line: {line}")

        return None  # No valid timestamp found

    raw_timestamp = match.group(0)  # Full timestamp string
    timezone_abbreviation = match.group(1)  # Extract timezone abbreviation

    try:
        # Parse the timestamp with the timezone info
        naive_dt = parser.parse(raw_timestamp, tzinfos=tzinfos)

        # Convert to local timezone (PDT) for display, instead of converting to UTC
        local_dt = naive_dt.astimezone(timezone_map[timezone_abbreviation])

        # Format the timestamp as YYYY-MM-DD HH:MM:SS
        formatted_timestamp = local_dt.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_timestamp
    except Exception as e:
        print(f"Error parsing timestamp '{raw_timestamp}': {e}")
        return None




########################################



##################################################
    

import re
from dateutil.parser import parse

# Optional timezone info
tzinfos = {
    "PDT": -7 * 3600, "PST": -8 * 3600, "EDT": -4 * 3600,
    "EST": -5 * 3600, "CDT": -5 * 3600, "CST": -6 * 3600,
    "MDT": -6 * 3600, "MST": -7 * 3600, "UTC": 0, "GMT": 0,
}

# Common timestamp patterns
timestamp_patterns = [
    r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}",                    # 2025-04-24 12:30:45
    r"[A-Z][a-z]{2} [A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2} [A-Z]{2,4} \d{4}",  # Tue Apr 07 00:41:44 PDT 2009
    r"\d{2}/\d{2}/\d{4}",                                         # 24/04/2025
    r"\d{4}/\d{2}/\d{2}",                                         # 2025/04/24
    r"\d{2}-\d{2}-\d{4}",                                         # 24-04-2025
]

def extract_timestamp_from_text(text):
    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return parse(match.group(), fuzzy=False, tzinfos=tzinfos)
            except Exception as e:
                print(f"❌ Failed to parse '{match.group()}': {e}")
    return None

##################################################

from dateutil.parser import parse

tzinfos = {
    "PDT": -7 * 3600,
    "PST": -8 * 3600,
    "EDT": -4 * 3600,
    "EST": -5 * 3600,
    "CDT": -5 * 3600,
    "CST": -6 * 3600,
    "MDT": -6 * 3600,
    "MST": -7 * 3600,
    "UTC": 0,
    "GMT": 0,
}

def extract_timestamp_from_text(text):
    try:
        return parse(text, fuzzy=True, tzinfos=tzinfos)
    except Exception as e:
        print(f"❌ Failed to parse: {e}")
        return None

##################################################

from collections import defaultdict
from datetime import datetime, timedelta

def group_by_time_scale_old_w(messages, time_scale='weekly'):
    grouped_messages = {}

    # List of potential timestamp formats
    timestamp_formats = [
        '%Y-%m-%d %H:%M:%S.%f',  # Format with microseconds
        '%Y-%m-%d %H:%M:%S',      # Format without microseconds
        '%Y-%m-%d %H:%M:%S.%f',   # Format with microseconds (fractional part)
        '%Y-%m-%dT%H:%M:%S.%f',   # ISO-like format with microseconds
        '%Y-%m-%dT%H:%M:%S'       # ISO-like format without microseconds
    ]

    for message in messages:
        timestamp = message[4]  # Assuming timestamp is in the message

        # Try parsing the timestamp with multiple formats
        parsed_timestamp = None
        for fmt in timestamp_formats:
            try:
                parsed_timestamp = datetime.strptime(str(timestamp), fmt)
                break  # Stop if we find a matching format
            except ValueError as e:
                continue  # Try the next format if this one fails

        if parsed_timestamp is None:
            logger.info(f"Error parsing timestamp for message: {message}")
            print(f"Error parsing timestamp for message: {message}")
            continue  # Skip this message if none of the formats work

        # Group messages based on time scale
        if time_scale == 'daily':
            period = parsed_timestamp.date()
        elif time_scale == 'weekly':
            start_of_week = parsed_timestamp - timedelta(days=parsed_timestamp.weekday())  # Monday of the week
            period = start_of_week.date()
        elif time_scale == 'monthly':
            period = f'{parsed_timestamp.year}-{parsed_timestamp.month}'
        elif time_scale == 'quarterly':
            quarter = (parsed_timestamp.month - 1) // 3 + 1
            period = f'{parsed_timestamp.year}-Q{quarter}'
        elif time_scale == 'yearly':
            period = f'{parsed_timestamp.year}'
        else:
            raise ValueError("Invalid time scale")

        # Group messages by the calculated period
        if period not in grouped_messages:
            grouped_messages[period] = []

        grouped_messages[period].append(message)

    #print(grouped_messages)  # Check the grouped messages
    logger.info(f"Grouped Messages", grouped_messages)


    return grouped_messages


################################################


from dateutil import parser
import pytz
import re

def extract_timestamp_from_text_Old_W(line):
    
    #Extracts and formats a timestamp from a single line of text.

    #Args: line (str): A single line of text containing a potential timestamp.

    #Returns: str or None: Formatted timestamp in 'YYYY-MM-DD HH:MM:SS' format, or None if no valid timestamp is found.
    
    # Define timezone mapping for PDT, EST, etc.
    timezone_map = {
        "PDT": pytz.timezone("US/Pacific"),
        "GMT": pytz.timezone("GMT"),
        "EST": pytz.timezone("US/Eastern"),
        "CST": pytz.timezone("US/Central"),
        "MST": pytz.timezone("US/Mountain"),
        "UTC": pytz.utc,
    }

    tzinfos = {tz: timezone_map[tz] for tz in timezone_map}

    # Define regex pattern for timestamps
    timestamp_regex = r"\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+(\w+)\s+\d{4}"

    # Find matches in the line
    match = re.search(timestamp_regex, line)

    if not match:
        
        print(f"Skipping line: No valid timestamp found. Line: {line}")
        logger.info(f"Skipping line: No valid timestamp found. Line: {line}")

        return None  # No valid timestamp found

    raw_timestamp = match.group(0)  # Full timestamp string
    timezone_abbreviation = match.group(1)  # Extract timezone abbreviation

    try:
        # Parse the timestamp with the timezone info
        naive_dt = parser.parse(raw_timestamp, tzinfos=tzinfos)

        # Convert to local timezone (PDT) for display, instead of converting to UTC
        local_dt = naive_dt.astimezone(timezone_map[timezone_abbreviation])

        # Format the timestamp as YYYY-MM-DD HH:MM:SS
        formatted_timestamp = local_dt.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_timestamp
    except Exception as e:
        print(f"Error parsing timestamp '{raw_timestamp}': {e}")
        return None
    
################################################

def extract_timestamp_from_text(line):
    timezone_map = {
        "PDT": pytz.timezone("US/Pacific"),
        "GMT": pytz.timezone("GMT"),
        "EST": pytz.timezone("US/Eastern"),
        "CST": pytz.timezone("US/Central"),
        "MST": pytz.timezone("US/Mountain"),
        "UTC": pytz.utc,
    }
    tzinfos = {tz: timezone_map[tz] for tz in timezone_map}

    # Try timezone-based format
    match = re.search(r"\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+(\w+)\s+\d{4}", line)
    if match:
        raw_timestamp = match.group(0)
        timezone_abbreviation = match.group(1)
        try:
            naive_dt = parser.parse(raw_timestamp, tzinfos=tzinfos)
            local_dt = naive_dt.astimezone(timezone_map[timezone_abbreviation])
            return local_dt
        except Exception as e:
            logger.warning(f"❌ Error parsing complex timestamp: {raw_timestamp} | {e}")

    # Try ISO date like 2025-01-01
    iso_match = re.search(r"\d{4}-\d{2}-\d{2}", line)
    if iso_match:
        try:
            return datetime.strptime(iso_match.group(), "%Y-%m-%d")
        except Exception as e:
            logger.warning(f"❌ Error parsing ISO timestamp: {line} | {e}")

    logger.info(f"Skipping line: No valid timestamp found. Line: {line[:80]}...")
    return None


###########################################
import re

def group_by_time_scale(data, time_scale='weekly'):
    
    #Group the data by the selected time scale (e.g., daily, weekly, monthly).
    #Accepts a string (large text), list of dicts, tuples, or strings.
    
    grouped_data = defaultdict(list)

    # === Handle large string input ===
    if isinstance(data, str):
        data = re.split(r'(?=\d{4}-\d{2}-\d{2})', data)

    for item in data:
        timestamp = None

        if isinstance(item, str):
            timestamp = extract_timestamp_from_text(item)
        elif isinstance(item, (tuple, list)) and len(item) > 4:
            timestamp = item[4]
        elif isinstance(item, dict):
            timestamp = item.get("timestamp")

        if not timestamp:
            logger.info(f"Skipping item due to missing timestamp: {str(item)[:80]}")
            continue

        # Group by time scale
        if time_scale == 'daily':
            period = timestamp.strftime('%Y-%m-%d')
        elif time_scale == 'weekly':
            period = timestamp.strftime('%Y-W%U')  # Week number of year
        elif time_scale == 'monthly':
            period = timestamp.strftime('%Y-%m')
        elif time_scale == 'quarterly':
            quarter = (timestamp.month - 1) // 3 + 1
            period = f"{timestamp.year}-Q{quarter}"
        else:
            logger.warning(f"⚠️ Unknown time scale: {time_scale}. Defaulting to monthly.")
            period = timestamp.strftime('%Y-%m')

        grouped_data[period].append(item)

    logger.info(f"✅ Grouped {len(data)} items into {len(grouped_data)} periods.")
    return dict(grouped_data)


########################################
"""
    
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np


def Trend_Predict_P_N_N_emotion_scores(comments):
    tokenizer = AutoTokenizer.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")
    model = AutoModelForSequenceClassification.from_pretrained("joeddav/distilbert-base-uncased-go-emotions-student")

    EMOTION_CLASSES = [
        "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", 
        "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
        "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
        "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
    ]

    emotion_5_classes = {
        'very_positive': {'joy', 'amusement', 'approval', 'excitement', 'gratitude', 'desire'},
        'positive': {'caring', 'pride', 'love', 'optimism', 'admiration'},
        'neutral': {'realization', 'curiosity', 'relief', 'confusion', 'surprise', 'neutral'},
        'negative': {'nervousness', 'sadness', 'grief', 'remorse'},
        'very_negative': {'anger', 'annoyance', 'disappointment', 'embarrassment', 'fear', 'disgust', 'disapproval'}
    }

    trenEmotionScores = {key: 0 for key in emotion_5_classes}

    texts = [comment[3] for comment in comments]

    try:
        if not texts:
            logger.warning("🚫 No text input provided to emotion model.")
            return [trenEmotionScores]

        inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)

        logits = outputs.logits
        probs = torch.softmax(logits, dim=1).detach().cpu().numpy()

        avg_probs = probs.mean(axis=0)
        logger.debug(f"🔢 Raw Output Shape: {probs.shape}")
        logger.debug(f"📊 Avg probs length: {len(avg_probs)}, values: {np.round(avg_probs, 3).tolist()}")

        for i, score in enumerate(avg_probs):
            label = EMOTION_CLASSES[i]
            for category, emotion_set in emotion_5_classes.items():
                if label in emotion_set:
                    trenEmotionScores[category] += score
                    break

        logger.info(f"✅ Final 5-class Emotion Scores: {trenEmotionScores}")

    except Exception as e:
        logger.error(f"❌ ERROR in emotion function: {str(e)}")

    return [trenEmotionScores]


########################################

def map_emotions_to_5_classes(emotion_list):
    mapping = {
        'very_negative': {'anger', 'annoyance', 'disappointment', 'embarrassment', 'fear', 'disgust', 'disapproval'},
        'negative': {'nervousness', 'sadness', 'grief', 'remorse'},
        'neutral': {'realization', 'curiosity', 'relief', 'confusion', 'neutral'},
        'positive': {'caring', 'pride', 'love', 'optimism', 'admiration'},
        'very_positive': {'joy', 'amusement', 'approval', 'excitement', 'gratitude', 'desire'}
    }

    counts = {k: 0 for k in mapping}

    for emotion in emotion_list:
        for category, group in mapping.items():
            if emotion in group:
                counts[category] += 1
                break

    return counts



########################################

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load the model and tokenizer (ensure the model fits your needs)
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def Trend_analyze_transformer_sentiment(text):
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch.nn.functional as F
    import torch

    model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)

    probs = F.softmax(outputs.logits, dim=-1).tolist()[0]  # Always a list

    predicted_index = probs.index(max(probs))
    predicted_score = probs[predicted_index]

    return [{
        "predicted_class": f"Class {predicted_index + 1}",
        "score": predicted_score,
        "all_scores": {f"Class {i+1}": prob for i, prob in enumerate(probs)}
    }]





########################################

import csv
from io import StringIO

def safe_extract_comment_text(item):
    try:
        parsed = next(csv.reader(StringIO(item)))
        if len(parsed) > 5:
            return parsed[5]
        else:
            logger.warning(f"⚠️ Less than 6 columns: {parsed}")
            return item  # fallback to raw
    except Exception as e:
        logger.warning(f"⚠️ Failed to parse item: {e}")
        return item  # fallback to raw



########################################
import csv
from io import StringIO

def create_trend_data(grouped_messages, time_scale):
    import logging
    trend_data = []
    logger.info(f"grouped messages are: {grouped_messages}")
    logger.info(f"Time scale is : {time_scale}")
    for period, group in grouped_messages.items():
        logging.debug(f"Processing period: {period}, number of messages: {len(group)}")

        logger.info(f"group in gropued_messages: {group}")
        logger.info(f"Items are : {grouped_messages.items}")
        # Extract messages


        text_data = []
        for item in group:
            try:
                # Parse CSV-style row (handling quoted commas)
                parsed = next(csv.reader(StringIO(item)))
                text_data = [safe_extract_comment_text(i).strip() for i in group]
            except Exception as e:
                logger.warning(f"⚠️ Failed to parse item: {e}")
        #text_data = [item[3] for item in group]
        logger.info(f"The Item text within CTD is {text_data}")
        clean_text = clean_extracted_text(" ".join(text_data))  # ✅ FIXED
        logger.info(f"\n\n\n\n: Clean text before chunking for Trend Data: Large Text: Single_Group:\n{clean_text}...\n\n\n")
            #chunks = chunk_sentences(clean_text, tokenizer=emotion_tokenizer)
        sentiment_chunks = chunk_sentences(clean_text, tokenizer=sentiment_tokenizer)
        if sentiment_chunks:
            for idx, chunk in enumerate(sentiment_chunks, 1):
                logger.info(f"Sentiment Chunks are: ")
                logger.info(f"🔢 Chunk {idx}: {chunk}")
        else:
            logger.info("❌ No Sentiment Chunks found.")

        emotion_chunks = chunk_sentences(clean_text, tokenizer=emotion_tokenizer)
        if sentiment_chunks:
            for idx, chunk in enumerate(emotion_chunks, 1):
                logger.info(f"Emotion Chunks are: ")
                logger.info(f"🔢 Chunk {idx}: {chunk}")
        else:
            logger.info("❌ No Sentiment Chunks found.")



        # Get sentiment scores
        try:
                      # 📊 Sentiment Analysis
            sentiment_scores = analyze_transformer_sentiment_chunks(sentiment_chunks)
            #sentiment_scores = Trend_analyze_transformer_sentiment(large_text)
            #sentiment_scores = Trend_analyze_transformer_sentiment(text_data)
            logging.debug(f"Sentiment scores for {period}: {sentiment_scores}")
        except Exception as e:
            logging.error(f"Error in sentiment analysis for {period}: {e}")
            sentiment_scores = []

        # Get emotion scores
        try:
            emotion_scores_list = Trend_Predict_P_N_N_emotion_scores(emotion_chunks)

            # ✅ DEBUG what's inside the list
            logger.debug(f"Raw emotion_scores_list: {emotion_scores_list}")

            # ✅ Aggregate scores into one dict
            emotion_scores = {}
            # Aggregate scores directly since each result is already flat
            emotion_scores = {}
            for result in emotion_scores_list:
                for emotion, score in result.items():
                    emotion_scores[emotion] = emotion_scores.get(emotion, 0) + score
            for i, result in enumerate(emotion_scores_list):
                logger.info(f"🔍 Emotion Result in create Emotion {i}: {result}")


            # Normalize
            total = sum(emotion_scores.values()) or 1
            emotion_scores = {k: v / total for k, v in emotion_scores.items()}
            logger.info(f"✅ Emotion Scores after summing & normalizing: {emotion_scores}")


            logging.debug(f"Emotion scores for {period}: {emotion_scores}")
        except Exception as e:
            logging.error(f"Error in emotion analysis for {period}: {e}")
            emotion_scores = {}

        # Skip if both scores are empty (could also choose to include partial)
        if not sentiment_scores and not emotion_scores:
            logging.warning(f"No valid scores for period {period}, skipping.")
            continue

        if not period or not period.strip():
            logger.warning(f"⚠️ Skipping entry with empty or invalid period: {period}")
            continue
        logger.debug(f"📆 Grouped period = {period}")

        trend_data.append({
            "period": str(period),
            "sentiment_scores": sentiment_scores,
            "emotion_scores": {
                "very_positive": round(emotion_scores.get("very_positive", 0), 3),
                "positive": round(emotion_scores.get("positive", 0), 3),
                "neutral": round(emotion_scores.get("neutral", 0), 3),
                "negative": round(emotion_scores.get("negative", 0), 3),
                "very_negative": round(emotion_scores.get("very_negative", 0), 3)
            }
        })


    #logging.debug(f"Final trend_data: {trend_data}")
    logger.info(f"Trebd Data: Final: {trend_data}  ")
    print("Final aggregated trend data (emotion):", trend_data)

    return trend_data


########################################

import matplotlib.pyplot as plt
import numpy as np

def plot_sentiment(trend_data):
    # Extract periods and sentiment scores dynamically from the trend_data
    periods = [entry['period'] for entry in trend_data]
    
    # If periods are datetime.date, just sort directly
    periods_sorted = sorted(periods)

    sentiment_counts = []

    # Build sentiment counts dynamically based on the actual data
    for entry in trend_data:
        sentiment_scores = entry.get('sentiment_scores', {})
        
        # Ensure 'all_scores' exists in the sentiment scores
        if 'all_scores' in sentiment_scores:
            sentiment_counts.append(list(sentiment_scores['all_scores'].values()))
        else:
            print(f"Warning: 'all_scores' not found for period: {entry['period']}")
            continue  # Skip this entry if 'all_scores' is missing

    sentiment_counts = np.array(sentiment_counts)

    # Ensure the data has a proper shape and format
    if sentiment_counts.ndim == 2 and sentiment_counts.size > 0:
        bar_width = 0.15
        index = np.arange(len(periods_sorted))  # Ensure periods_sorted is used for X-axis

        fig, ax = plt.subplots(figsize=(10, 6))

        # Loop through the sentiment classes (columns) and plot them
        for i in range(sentiment_counts.shape[1]):
            ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')

        ax.set_xlabel('Period')
        ax.set_ylabel('Sentiment Scores')
        ax.set_title('Sentiment Analysis Trend')

        # Set the X-ticks to the sorted periods dynamically
        ax.set_xticks(index + 2 * bar_width)
        ax.set_xticklabels([str(period) for period in periods_sorted], rotation=45)  # Convert periods to string if needed

        ax.legend()

        plt.tight_layout()

        return fig
    else:
        print("No valid sentiment data to plot.")
        return None


########################################

import matplotlib.pyplot as plt
import numpy as np

def plot_sentiment_0(trend_data):
    print(f"Trend Data: {trend_data}")  # This will help check if the trend_data is populated
    periods = [entry['period'] for entry in trend_data]
    
    sentiment_counts = []
    for entry in trend_data:
        sentiment_scores = entry.get('sentiment_scores', {})
        
        # Skip entries with missing or invalid 'all_scores'
        if isinstance(sentiment_scores, dict) and 'all_scores' in sentiment_scores:
            sentiment_counts.append(list(sentiment_scores['all_scores'].values()))
        else:
            print(f"Skipping invalid sentiment_scores structure for entry: {entry}")
            continue  # Skip this entry if 'all_scores' is missing or invalid

    # Check the shape and length of the sentiment counts
    print(f"Sentiment counts: {sentiment_counts}")

    if len(sentiment_counts) == 0:
        print("No valid sentiment data to plot.")
        return None  # Return None if no valid data is available

    sentiment_counts = np.array(sentiment_counts)

    # Create the plot
    bar_width = 0.15
    index = np.arange(len(periods))

    fig, ax = plt.subplots(figsize=(12, 8))

    for i in range(sentiment_counts.shape[1]):  # Loop over sentiment classes
        ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')

    ax.set_xlabel('Time Period', fontsize=12)
    ax.set_ylabel('Sentiment Count', fontsize=12)
    ax.set_title('Sentiment Analysis Trend', fontsize=14)
    ax.set_xticks(index + 2 * bar_width)
    ax.set_xticklabels(periods, rotation=45, ha='right', fontsize=10)
    ax.legend()

    plt.tight_layout()

    return fig  # Return the figure for rendering


########################################


def validate_date_range(start_date, end_date):
    # Ensure both dates are provided
    if not start_date or not end_date:
        raise ValueError("Start date and end date are required.")
    
    today = datetime.today().date()  # Get today's date
    
    # Check if start_date and end_date are in the correct range
    if start_date > today or end_date > today:
        raise ValueError("Dates cannot be in the future.")
    
    if start_date > end_date:
        raise ValueError("Start date cannot be later than end date.")





########################################

def perform_sentiment_analysis(messages):
    # Placeholder for sentiment analysis (e.g., using transformer model)
    # Let's assume each message returns sentiment (positive, neutral, negative)
    sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for message in messages:
        # Assume the sentiment analysis returns a positive/neutral/negative sentiment for the message
        sentiment = 'positive'  # Placeholder; replace with actual model prediction
        sentiment_scores[sentiment] += 1

    return sentiment_scores

def Predict_P_N_N_emotion_scores(messages):
    # Placeholder for emotion detection (P, N, N = Positive, Negative, Neutral)
    emotion_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for message in messages:
        # Placeholder for emotion categorization
        emotion = 'positive'  # Placeholder; replace with actual emotion categorization
        emotion_scores[emotion] += 1
    
    return emotion_scores


########################################

def sort_trend_data(data_list):
    return sorted(data_list, key=lambda x: parse_period(x["period"]))

########################################


from datetime import datetime
import re

def parse_period(period_str):
    import re
    from datetime import datetime

    # Daily: 2024-04-12
    if re.match(r"\d{4}-\d{2}-\d{2}", period_str):
        return datetime.strptime(period_str, "%Y-%m-%d")

    # Weekly: 2024-W14
    elif re.match(r"\d{4}-W\d{1,2}", period_str):
        year, week = map(int, re.findall(r"\d+", period_str))
        return datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")

    # Monthly padded: 2024-12
    elif re.match(r"\d{4}-\d{2}$", period_str):
        return datetime.strptime(period_str, "%Y-%m")

    # Monthly unpadded: 2024-6 → pad to 2024-06
    elif re.match(r"\d{4}-\d{1}$", period_str):
        parts = period_str.split("-")
        return datetime.strptime(f"{parts[0]}-{int(parts[1]):02d}", "%Y-%m")

    # Quarterly: 2024-Q3
    elif re.match(r"\d{4}-Q\d", period_str):
        year, quarter = map(int, re.findall(r"\d+", period_str))
        month = (quarter - 1) * 3 + 1
        return datetime(year, month, 1)

    # Yearly: 2024
    elif re.match(r"\d{4}$", period_str):
        return datetime.strptime(period_str, "%Y")

    return datetime.min  # fallback



#plot_trend_data

"""

import matplotlib.pyplot as plt
import numpy as np

def plot_sentiment_1(trend_data):
    print(f"Trend Data: {trend_data}")  # This will help check if the trend_data is populated
    periods = [entry['period'] for entry in trend_data]
    
    sentiment_counts = []
    for entry in trend_data:
        sentiment_scores = entry.get('sentiment_scores', {})
        
        # Skip entries with missing or invalid 'all_scores'
        if isinstance(sentiment_scores, dict) and 'all_scores' in sentiment_scores:
            sentiment_counts.append(list(sentiment_scores['all_scores'].values()))
        else:
            print(f"Skipping invalid sentiment_scores structure for entry: {entry}")
            continue  # Skip this entry if 'all_scores' is missing or invalid

    # Check the shape and length of the sentiment counts
    print(f"Sentiment counts: {sentiment_counts}")

    if len(sentiment_counts) == 0:
        print("No valid sentiment data to plot.")
        return None  # Return None if no valid data is available

    sentiment_counts = np.array(sentiment_counts)

    # Create the plot
    bar_width = 0.15
    index = np.arange(len(periods))

    fig, ax = plt.subplots(figsize=(10, 6))

    for i in range(sentiment_counts.shape[1]):  # Loop over sentiment classes
        ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')

    ax.set_xlabel('Time Period')
    ax.set_ylabel('Sentiment Count')
    ax.set_title('Sentiment Analysis Trend')
    ax.set_xticks(index + 2 * bar_width)
    ax.set_xticklabels(periods)
    ax.legend()

    plt.tight_layout()

    return fig  # Return the figure for rendering

import matplotlib.pyplot as plt
import numpy as np

def plot_sentiment(trend_data):
    periods = [entry['period'] for entry in trend_data]
    sentiment_counts = []

    for entry in trend_data:
        sentiment_scores = entry['sentiment_scores']['all_scores']
        sentiment_counts.append(list(sentiment_scores.values()))

    sentiment_counts = np.array(sentiment_counts)
    
    # Ensure the data has a proper shape and format
    if sentiment_counts.ndim == 2:
        bar_width = 0.15
        index = np.arange(len(periods))
        fig, ax = plt.subplots(figsize=(10, 6))

        for i in range(sentiment_counts.shape[1]):
            ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')

        ax.set_xlabel('Period')
        ax.set_ylabel('Sentiment Scores')
        ax.set_title('Sentiment Analysis Trend')
        ax.set_xticks(index + 2 * bar_width)
        ax.set_xticklabels(periods, rotation=45)
        ax.legend()

        plt.tight_layout()

        return fig
    else:
        return None

"""

    # You can similarly create a second plot for emotion scores if needed
    # For example:
    # ax.bar(x, emotion_positive, width=bar_width, label='Emotion Positive', color='lightgreen')
    # ax.bar([p + bar_width for p in x], emotion_neutral, width=bar_width, label='Emotion Neutral', color='lightgrey')
    # ax.bar([p + 2*bar_width for p in x], emotion_negative, width=bar_width, label='Emotion Negative', color='lightcoral')
    # plt.show()


import numpy as np

def create_trend_data_0(grouped_messages, time_scale):
    trend_data = []
    
    for period, messages in grouped_messages.items():
        # Extract just the text from the messages (i.e., the 4th element in each tuple)
        text_data = [message[3] for message in messages]  # Extract text (message[3])
        
        # Call the transformer-based sentiment analysis
        sentiment_scores = Trend_analyze_transformer_sentiment(text_data)
        
        # Now aggregate the sentiment data by averaging over the messages
        # Ensure each score is numeric and correctly averaged
        if sentiment_scores:  # Make sure sentiment_scores is not empty
            # Extract the labels from the first sentiment score dictionary (assuming all have the same labels)
            labels = list(sentiment_scores[0]['all_scores'].keys())

            # Aggregate the sentiment scores by calculating the mean of each label across all messages
            aggregated_sentiment_scores = {
                "all_scores": {label: np.mean([score['all_scores'][label] for score in sentiment_scores]) for label in labels}
            }

            # Prepare trend data
            trend_data.append({
                'period': period,
                'sentiment_scores': aggregated_sentiment_scores
                # 'emotion_scores': emotion_scores  # Uncomment if you have emotion scores
            })

    return trend_data
