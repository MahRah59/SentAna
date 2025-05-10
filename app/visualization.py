import plotly.express as px
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from math import pi



import logging
logger = logging.getLogger(__name__)
logger.info("Something happened")

########################################

def generate_custom_colored_pie_chart(sentiment, model_type='vader'):
    if model_type == 'transformer' and "all_scores" in sentiment:
        color_order = ['1 star', '2 stars', '3 stars', '4 stars', '5 stars']
        color_map = {
            '1 star': 'red',
            '2 stars': 'gold',
            '3 stars': 'lightgrey',
            '4 stars': '#0073e6',
            '5 stars': 'green'
        }
        values = [sentiment['all_scores'][label] for label in color_order if label in sentiment['all_scores']]
        labels = [label for label in color_order if label in sentiment['all_scores']]

    elif model_type == 'vader':
        color_order = ['Negative', 'Neutral', 'Positive']
        color_map = {
            'Positive': 'green',
            'Neutral': 'lightgrey',
            'Negative': 'red'
        }
        values = [sentiment['neg'], sentiment['neu'], sentiment['pos']]
        labels = color_order

    else:
        return None

    colors = [color_map.get(label, '#cccccc') for label in labels]

    # ❌ Removed category_orders={"names": labels}
    fig = px.pie(
        names=labels,
        values=values,
        color=labels,
        color_discrete_map=color_map
    )
    return fig.to_html(full_html=False)


########################################

def generate_visualizations(sentiment, text, basic_display_option):
    pie_chart = None
    gauge_chart = None
    word_cloud_img = None

    if basic_display_option in ['pie_chart', 'all']:
        model_type = 'transformer' if 'all_scores' in sentiment else 'vader'
        pie_chart = generate_custom_colored_pie_chart(sentiment, model_type)

    if basic_display_option in ['compound', 'all']:
        fig = px.bar(
            x=['Compound'], 
            y=[sentiment['compound'] if "compound" in sentiment else sentiment['predicted_score']],
            title='Sentiment Gauge'
        )

    if basic_display_option in ['gauge', 'all']:
        gauge_chart = generate_gauge_chart(sentiment)

    if basic_display_option in ['word_cloud', 'all']:
        wordcloud = WordCloud().generate(text)
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        word_cloud_img = base64.b64encode(img.getvalue()).decode('utf-8')

    return pie_chart, gauge_chart, word_cloud_img

########################################

def generate_bar_chart_emotion(Sentiment_emotions, title="Emotion Scores"):
    fig, ax = plt.subplots(figsize=(8, max(6, 0.3 * len(Sentiment_emotions))))  # Dynamic height

    if isinstance(Sentiment_emotions, dict):
        labels = list(Sentiment_emotions.keys())
        scores = list(Sentiment_emotions.values())

        ax.barh(labels, scores)
        ax.set_xlabel('Scores')
        ax.set_title(title)
        plt.tight_layout()  # Adjusts padding automatically

    else:
        raise ValueError("Input data for bar chart must be a dictionary.")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return chart_data
########################################

def generate_bar_chart(Sentiment_emotions, title="Scores"):
    num_items = len(Sentiment_emotions)
    fig_height = max(4, 0.3 * num_items)
    fig, ax = plt.subplots(figsize=(8, fig_height))

    if isinstance(Sentiment_emotions, dict):
        labels = list(Sentiment_emotions.keys())
        scores = list(Sentiment_emotions.values())

        if num_items > 8:  # ✅ Horizontal if many bars
            ax.barh(labels, scores)
            ax.set_xlabel('Scores')
        else:  # ✅ Vertical if fewer bars
            ax.bar(labels, scores)
            ax.set_ylabel('Scores')
            plt.xticks(rotation=0, fontsize=9)

        ax.set_title(title)
        plt.tight_layout()

    else:
        raise ValueError("Input data for bar chart must be a dictionary.")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return chart_data


########################################

def generate_bar_chart_trend(aggregated_trend_data):
    periods = [entry['period'] for entry in aggregated_trend_data]
    sentiment_counts = []
    for entry in aggregated_trend_data:
        sentiment_scores = entry['sentiment_scores']
        formatted_scores = [round(score, 2) for score in sentiment_scores.values()]  # Limit to 2 decimals
        sentiment_counts.append(formatted_scores)
    sentiment_counts = np.array(sentiment_counts)
    if sentiment_counts.ndim == 2:
        bar_width = 0.15
        index = np.arange(len(periods))
        fig, ax = plt.subplots(figsize=(10, 6))
        for i in range(sentiment_counts.shape[1]):
            ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')
        ax.set_xlabel('Period', fontsize=12, fontweight='bold')
        ax.set_ylabel('Sentiment Scores', fontsize=12, fontweight='bold')
        ax.set_title('Sentiment Trend Over Time', fontsize=12, fontweight='bold')
        ax.set_xticks(index + 2 * bar_width)
        ax.set_xticklabels(periods, rotation=5, ha='right')
        ax.legend()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        return chart_data
    else:
        return None

########################################

def generate_radar_chart(sentiment_scores, title=""):
    labels = list(sentiment_scores.keys())
    values = list(sentiment_scores.values())
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.25)
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(title, size=14, color='blue')
    ax.set_title(title, pad=15)  # pad value controls space below title

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    radar_chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return radar_chart_data


########################################

def generate_gauge_chart(sentiment):
    score = sentiment.get("compound", sentiment.get("predicted_score", 0))
    is_vader = "compound" in sentiment
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        #title={'text': "Sentiment Score"},
        gauge={
            'axis': {'range': [-1, 1] if is_vader else [0, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.5] if is_vader else [0, 0.2], 'color': "red"},
                {'range': [-0.5, 0] if is_vader else [0.2, 0.4], 'color': "orange"},
                {'range': [0, 0.5] if is_vader else [0.4, 0.6], 'color': "lightgray"},
                {'range': [0.5, 1] if is_vader else [0.6, 1], 'color': "green"},
            ],
        }
    ))
    return fig.to_html(full_html=False)

########################################

def generate_word_cloud(comments):
    wordcloud = WordCloud(width=500, height=300, background_color='white').generate(comments)
    buf = BytesIO()
    wordcloud.to_image().save(buf, format='PNG')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return chart_data


########################################

import matplotlib.pyplot as plt
import io
import base64

def generate_emotion_trend_chart(data):
    import matplotlib.pyplot as plt
    import io
    import base64

    periods = [entry['period'] for entry in data]
    very_positive = [entry['very_positive'] for entry in data]
    positive = [entry['positive'] for entry in data]
    neutral = [entry['neutral'] for entry in data]
    negative = [entry['negative'] for entry in data]
    very_negative = [entry['very_negative'] for entry in data]

    x = range(len(periods))
    width = 0.15

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar([p - 2*width for p in x], very_positive, width, label='Very Positive')
    ax.bar([p - width for p in x], positive, width, label='Positive')
    ax.bar(x, neutral, width, label='Neutral')
    ax.bar([p + width for p in x], negative, width, label='Negative')
    ax.bar([p + 2*width for p in x], very_negative, width, label='Very Negative')

    ax.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Emotion Score', fontsize=12, fontweight='bold')
    ax.set_title('Emotion Trend Over Time', fontsize=12, fontweight='bold')
    ax.set_xticklabels(periods, rotation=10, ha='right')
    ax.set_xticks(x)
    ax.set_xticklabels(periods)
    ax.legend()

    # Convert plot to base64 image
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    return img_base64



########################################

"""
# THE OLD VISUALIZATION 
########################################
########################################
########################################
########################################
########################################
########################################
########################################
########################################
# Other imports
import plotly.express as px
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.graph_objects as go


########################################

# Define generate_visualizations function
def generate_visualizations(sentiment, text, basic_display_option):
    pie_chart = None
    gauge_chart = None
    word_cloud_img = None

    if basic_display_option in ['pie_chart', 'all']:
        if "all_scores" in sentiment:  # Transformer output
            values = list(sentiment["all_scores"].values())
            labels = list(sentiment["all_scores"].keys())
            #print("Values in all scores are :", values)
        else:  # VADER output
            values = [sentiment['pos'], sentiment['neu'], sentiment['neg']]
            labels = ['Positive', 'Neutral', 'Negative']
            #print("Values in VADER OUTPUT are :", values)

        
        fig = px.pie(names=labels, values=values, title='Sentiment Distribution')
        pie_chart = fig.to_html(full_html=False)

    if basic_display_option in ['compound', 'all']:
        fig = px.bar(
            x=['Compound'], 
            y=[sentiment['compound'] if "compound" in sentiment else sentiment['predicted_score']],
            title='Sentiment Gauge'
        )
        #gauge_chart = fig.to_html(full_html=False)

    if basic_display_option in ['gauge', 'all']:
        gauge_chart = generate_gauge_chart(sentiment)
    
    if basic_display_option in ['word_cloud', 'all']:
        wordcloud = WordCloud().generate(text)
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        word_cloud_img = base64.b64encode(img.getvalue()).decode('utf-8')

    return pie_chart, gauge_chart, word_cloud_img


import matplotlib.pyplot as plt
from io import BytesIO
import base64

########################################

def generate_bar_chart(Sentiment_emotions):
    # Sentiment_emotions should be a dictionary like { 'positive': 0.8, 'neutral': 0.1, 'negative': 0.1 }
    fig, ax = plt.subplots()
    
    # Ensure Sentiment_emotions has valid keys and values
    if isinstance(Sentiment_emotions, dict):
        ax.bar(Sentiment_emotions.keys(), Sentiment_emotions.values())
        ax.set_ylabel('Scores')
        ax.set_title('Sentiment Scores')
        plt.xticks(rotation=45, ha='right')
    else:
        raise ValueError("Input data for bar chart must be a dictionary with sentiment labels and scores.")

    # Save chart to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return chart_data


########################################

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def generate_bar_chart_trend(aggregated_trend_data):
    Generate a bar chart for aggregated trend data
    periods = [entry['period'] for entry in aggregated_trend_data]

    sentiment_counts = []

    for entry in aggregated_trend_data:
        sentiment_scores = entry['sentiment_scores']
        
        # Debugging: print sentiment_scores before processing
        print(f"Sentiment scores for {entry['period']}: {sentiment_scores}")
        
        sentiment_counts.append(list(sentiment_scores.values()))

    sentiment_counts = np.array(sentiment_counts)

    if sentiment_counts.ndim == 2:
        bar_width = 0.15
        index = np.arange(len(periods))
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the bars for each class
        for i in range(sentiment_counts.shape[1]):
            ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')

        ax.set_xlabel('Period')
        ax.set_ylabel('Sentiment Scores')
        ax.set_title('Sentiment Analysis Trend')
        ax.set_xticks(index + 2 * bar_width)
        ax.set_xticklabels(periods, rotation=45)
        ax.legend()

        # Save chart to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        #print ("The Chart Data is : ", chart_data)
        buf.close()

        # Return chart data
        return chart_data
    else:
        print("Sentiment counts array is not 2D.")
        return None
    

########################################
    
import numpy as np
import matplotlib.pyplot as plt
from math import pi

def generate_radar_chart(sentiment_scores):
    
    Generate a radar chart for sentiment scores.
    sentiment_scores should be a dictionary with sentiment categories as keys and scores as values.
    

    # Define the labels (sentiment categories)
    labels = list(sentiment_scores.keys())
    values = list(sentiment_scores.values())

    # Compute the angle of each axis
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

    # Make the plot a circular plot
    values += values[:1]  # Repeat the first value to close the circle
    angles += angles[:1]

    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.25)
    ax.plot(angles, values, color='blue', linewidth=2)

    # Set labels
    ax.set_yticklabels([])  # Hide y-axis ticks
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    # Title
    ax.set_title('Sentiment Analysis Radar Chart', size=14, color='blue')

    # Save the chart to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert image to base64
    radar_chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return radar_chart_data


########################################

import plotly.graph_objects as go

def generate_gauge_chart(sentiment):
    score = sentiment.get("compound", sentiment.get("predicted_score", 0))
    is_vader = "compound" in sentiment

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Sentiment Score"},
        gauge={
            'axis': {'range': [-1, 1] if is_vader else [0, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.5] if is_vader else [0, 0.2], 'color': "red"},
                {'range': [-0.5, 0] if is_vader else [0.2, 0.4], 'color': "orange"},
                {'range': [0, 0.5] if is_vader else [0.4, 0.6], 'color': "lightgray"},
                {'range': [0.5, 1] if is_vader else [0.6, 1], 'color': "green"},
            ],
        }
    ))

    return fig.to_html(full_html=False)

########################################

from wordcloud import WordCloud

def generate_word_cloud(comments):
    
    Generate a word cloud from the comments.
    `comments` is a list of strings.
    
    #text = " ".join(comments)
    wordcloud = WordCloud(width=500, height=300, background_color='white').generate(comments)

    # Save word cloud to a BytesIO object
    buf = BytesIO()
    wordcloud.to_image().save(buf, format='PNG')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return chart_data

########################################








########################################
########################################
########################################
########################################
########################################

def generate_emotion_visualizations(emotions):
    Generate visualizations for emotion scores.
    # Bar Chart
    bar_chart_img = io.BytesIO()
    labels = list(emotions.keys())
    scores = list(emotions.values())

    plt.figure(figsize=(8, 4))
    plt.bar(labels, scores, color='skyblue')
    plt.title("Emotion Scores (Bar Chart)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(bar_chart_img, format='png')
    bar_chart_img.seek(0)
    bar_chart_url = base64.b64encode(bar_chart_img.getvalue()).decode()

    # Radar Chart
    radar_chart_img = io.BytesIO()
    plt.figure(figsize=(6, 6))
    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    scores += scores[:1]
    angles += angles[:1]
    plt.polar(angles, scores, marker='o', color='orange')
    plt.fill(angles, scores, alpha=0.25, color='orange')
    plt.title("Emotion Scores (Radar Chart)")
    plt.xticks(angles[:-1], labels, color='black')
    plt.tight_layout()
    plt.savefig(radar_chart_img, format='png')
    radar_chart_img.seek(0)
    radar_chart_url = base64.b64encode(radar_chart_img.getvalue()).decode()

    return f"data:image/png;base64,{bar_chart_url}", f"data:image/png;base64,{radar_chart_url}"

########################################


def generate_intent_visualizations(results):
    # Pie chart
    labels = [item['class'] for item in results['intents']]
    sizes = [item['score'] for item in results['intents']]
    
    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title("Intent Distribution")
    pie_chart = save_chart_to_base64()

    return {"pie_chart": pie_chart}
    
def save_chart_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()
    return img_base64

########################################


def visualize_trend_data_0(trend_data):
    # Prepare data for visualization
    periods = [data['period'] for data in trend_data]
    sentiment_positive = [data['sentiment_scores']['positive'] for data in trend_data]
    sentiment_neutral = [data['sentiment_scores']['neutral'] for data in trend_data]
    sentiment_negative = [data['sentiment_scores']['negative'] for data in trend_data]

    # Create bar chart
    fig = px.bar(
        x=periods,
        y=[sentiment_positive, sentiment_neutral, sentiment_negative],
        labels={'x': 'Time Period', 'y': 'Sentiment Count'},
        title='Sentiment Trend Analysis',
        barmode='stack',
        color_discrete_sequence=['green', 'grey', 'red']
    )

    fig.show()

    return fig


########################################


def visualize_trend_data(trend_data):
    periods = [entry['period'] for entry in trend_data]
    sentiment_counts = []

    for entry in trend_data:
        sentiment_scores = entry.get('sentiment_scores', {})
        
        if 'all_scores' in sentiment_scores:
            sentiment_counts.append(list(sentiment_scores['all_scores'].values()))
        else:
            print(f"Warning: 'all_scores' not found for period: {entry['period']}")
            continue  # Skip this entry if 'all_scores' is missing

    sentiment_counts = np.array(sentiment_counts)

    # Aggregate sentiment scores by period
    aggregated_sentiments_emotions = {}
    if sentiment_counts.ndim == 2 and sentiment_counts.size > 0:
        # Loop over the periods and aggregate
        for i, period in enumerate(periods):
            aggregated_sentiments_emotions[period] = {
                f"Class {i+1}": np.mean(sentiment_counts[:, i]) for i in range(sentiment_counts.shape[1])
            }

        # Return the aggregated data as a dictionary
        return aggregated_sentiments_emotions
    else:
        print("No valid sentiment data to plot.")
        return None


########################################
########################################
########################################
########################################
########################################

import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO



# Function to generate the chart (as already written)
def generate_bar_chart_trend_2(aggregated_trend_data):


    aggregated_trend_data = [
    {'period': '2024-11-18', 'sentiment_scores': {'Class 1': 0.10298888180404901, 'Class 2': 0.1301941683748737, 'Class 3': 0.21622799513861538, 'Class 4': 0.2081051640212536, 'Class 5': 0.3424837972503155}},
    {'period': '2024-12-02', 'sentiment_scores': {'Class 1': 0.11716125926209821, 'Class 2': 0.17045098733743308, 'Class 3': 0.2640250712995314, 'Class 4': 0.15685545823847255, 'Class 5': 0.2915072279671828}},
    {'period': '2024-12-30', 'sentiment_scores': {'Class 1': 0.08609573380090296, 'Class 2': 0.11120198941789568, 'Class 3': 0.14771622768603265, 'Class 4': 0.19488792729874452, 'Class 5': 0.4600981183660527}}
        ]
    Generate a bar chart for aggregated trend data
    periods = [entry['period'] for entry in aggregated_trend_data]
    sentiment_counts = []

    for entry in aggregated_trend_data:
        sentiment_scores = entry['sentiment_scores']
        sentiment_counts.append(list(sentiment_scores.values()))

    sentiment_counts = np.array(sentiment_counts)

    if sentiment_counts.ndim == 2:
        bar_width = 0.15
        index = np.arange(len(periods))
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the bars for each class
        for i in range(sentiment_counts.shape[1]):
            ax.bar(index + i * bar_width, sentiment_counts[:, i], bar_width, label=f'Class {i+1}')

        ax.set_xlabel('Period')
        ax.set_ylabel('Sentiment Scores')
        ax.set_title('Sentiment Analysis Trend')
        ax.set_xticks(index + 2 * bar_width)
        ax.set_xticklabels(periods, rotation=45)
        ax.legend()

        # Save chart to a BytesIO object
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()

        # Return chart data
        return chart_data
    else:
        return None




########################################
        
        """