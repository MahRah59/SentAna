# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import TextAreaField, RadioField, FileField, DateField
from wtforms.validators import Optional
from email_validator import validate_email, EmailNotValidError
from wtforms import SelectField, URLField, BooleanField
from wtforms import DecimalField, IntegerField
from wtforms.fields import URLField


##########################################

class TransformerForm(FlaskForm):
    platform = SelectField(
        'Select Platform:',
        choices=[
            ('twitter', 'Twitter/X'),
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('youtube', 'YouTube')
        ],
        validators=[DataRequired()]
    )
    twitter_handle = StringField('Twitter Handle or Hashtag:', validators=[Optional()])
    tweet_url = URLField('Tweet URL:', validators=[Optional()])
    facebook_page = StringField('Facebook Page Name:', validators=[Optional()])
    facebook_post = URLField('Facebook Post URL:', validators=[Optional()])
    instagram_account = StringField('Instagram Username:', validators=[Optional()])
    instagram_post = URLField('Instagram Post URL:', validators=[Optional()])
    youtube_video = URLField('YouTube Video URL:', validators=[Optional()])
    youtube_channel = StringField('YouTube Channel Name:', validators=[Optional()])
    submit_transformer = SubmitField('Analyze')

##########################################

class VaderForm(FlaskForm):
    text = TextAreaField('Enter text to analyze', validators=[DataRequired()])
    display = RadioField('Select Display Option', choices=[
        ('text', 'Text'),
        ('pie_chart', 'Pie Chart'),
        ('gauge', 'Gauge'),
        ('word_cloud', 'Word Cloud'),
        ('all', 'Show All')
    ], default='text')
    submit_vader = SubmitField('Analyze VADER')

##########################################

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=40)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional()])

    role = SelectField('Role', choices=[
        ('customer', 'Customer'),
        ('sentanaUser', 'SentAna User'),
        ('employee', 'Employee'),
        ('crm_admin', 'CRM Admin')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

##########################################

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

##########################################

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class MocSentimentAnalysis (FlaskForm):
    platform = RadioField(' Select Moc_Platform', choices=[('input_type', 'Select Input Type'),
                                                     ('value', 'Select Input Value')],                                                    
                          validators=[Optional()])

##########################################

class OrderForm(FlaskForm):
    order_id = StringField('Order ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('purchased', 'Purchased'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('other', 'Under Processing')
   ], validators=[DataRequired()])
    purchase_date =  StringField('Purchased Delivery Time', validators=[Optional()])
    Shipped_date = StringField('Estimated Delivery Time', validators=[Optional()])
    Delivery_date = StringField('Estimated Delivery Time', validators=[DataRequired()])
    submit = SubmitField('Update Order')
    
##########################################

class ServiceForm(FlaskForm):
    service_type = StringField('Service Type', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    additional_information = StringField('Additional Information', validators=[Optional()])
    availability = StringField('Availability', validators=[DataRequired()])
    submit = SubmitField('Update Service')

##########################################

class ProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    specifications = StringField('Specifications', validators=[DataRequired()])
    additional_information = StringField('Additional Information', validators=[Optional()])
    release_date = StringField('Release Date', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    submit = SubmitField('Update Product')

##########################################

class SentimentAnalysisForm(FlaskForm):
    analysis_mode = RadioField(
        'Analysis Mode',
        choices=[('basic', 'Basic Analysis'), ('advanced', 'Advanced Analysis')],
        default='basic',
        validators=[DataRequired()]
    )

    # Social Media Platform Selection
    platform = RadioField('Social Media Platform', choices=[
        ('internet_articles', 'Internet Articles'),
        ('file', 'File/Dataset'),
        ('twitter', 'Twitter/X'),
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram')
    ], validators=[DataRequired()]
    )

    # 📌 **Step 2: Fields for "Internet Articles/Information"**
    company_name=StringField('Company Name', validators=[Optional()])
    pasted_article_text = TextAreaField('Paste Article Text Here', validators=[Optional()])
    preferred_sources = TextAreaField('Preferred Sources (URLs, one per line)', validators=[Optional()])
    keywords = StringField('Keywords', validators=[Optional()])
    exclusion_criteria = TextAreaField('Exclude Words/URLs (optional)', validators=[Optional()])

    # 📌 **Step 3: Time-based filtering**
    time_filter = SelectField('Time Range', choices=[
        ('any', 'Any Time'),
        ('24h', 'Last 24 Hours'),
        ('7d', 'Last 7 Days'),
        ('30d', 'Last 30 Days')
    ], validators=[Optional()])
    
    trend_time_scale = SelectField('Trend Time Scale', choices=[
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], validators=[Optional()])

    file_upload = FileField('Upload File(s): CSV, TXT or PDF', validators=[Optional()])
    large_text = TextAreaField('Paste Large Text Here', validators=[Optional()])

    # Twitter Sub-fields
    twitter_handle = StringField('Twitter Handle or Hashtag', validators=[Optional()])
    #twitter_text = TextAreaField('Tweet Text', validators=[Optional()])
    twitter_url = URLField('Tweet URL', validators=[Optional()])
    twitter_Mock_text = TextAreaField('Tweet Mock Text', validators=[Optional()])



    # YouTube Sub-fields
    youtube_channel = StringField('YouTube Channel Name', validators=[Optional()])
    youtube_video = URLField('YouTube Video URL', validators=[Optional()])
    #youtube_text = TextAreaField('YouTube Text Input', validators=[Optional()])
    #youtube_Mock_video = URLField('YouTube Mock Video URL', validators=[Optional()])
    youtube_Mock_channel = StringField('YouTube Mock Channel ', validators=[Optional()])


    # Facebook Sub-fields
    facebook_page = StringField('Facebook Page Name', validators=[Optional()])
    facebook_post = URLField('Facebook Post URL', validators=[Optional()])
    #facebook_text = TextAreaField('Facebook Text Input', validators=[Optional()])

    # Instagram Sub-fields
    instagram_account = StringField('Instagram Username', validators=[Optional()])
    instagram_post = URLField('Instagram Post URL', validators=[Optional()])
    #instagram_text = TextAreaField('Instagram Text Input', validators=[Optional()])

    # BAsic Analysis Fields
    basic_analysis_type = RadioField('Select Analysis Type', choices=[
        ('vader', 'VADER (Rule-Based)'),
        ('transformer', 'Transformer (Deep Learning-Based)')
        #('Mock_data', 'Mock_data')
        ], validators=[Optional()])


    # Advanced Analysis Fields (initially hidden via JavaScript)
    advanced_analysis_type = RadioField('Select Analysis Type', choices=[
        ('emotion_detection', 'Emotion Detection'),
        ('intent_classification', 'Intent Classification'),
        ('trend_analysis', 'Sentiment Trend Analysis'),
        ('absa', 'Aspect-Based Sentiment Analysis'),
        ('multilingual', 'Multilingual Sentiment Analysis')
    ], validators=[Optional()])

    # Sentiment Trend Analysis embedded choices (initially hidden)
    sentiment_trend_analysis_type = RadioField('Select Sentiment Trend Type', choices=[
        ('overall_sentiment_trend_analysis', 'Overall Sentiment Trend Analysis'),
        ('chat_session_sentiment_analysis', 'Chat Session Sentiment Analysis'),
        ('aspect_based_analysis', 'Aspect-Based Sentiment Analysis'),
        ('other_custom_analysis', 'Other Custom Analysis')
    ], validators=[Optional()])
    sentiment_trend_analysis_type.render_kw = {'style': 'display:none;'}  # Initially hidden

    # Field for aspect input with placeholder text
    aspect_input = StringField(
        'Enter Aspect(s) to Analyze',
        validators=[Optional()],
        render_kw={"placeholder": "Enter Aspect(s) to Analyze: e.g., battery life, screen quality, etc."}  # Adding placeholder
    )
    chatbot_message = TextAreaField('Type a message to the chatbot:', validators=[Optional()])
    
    intent_classification_type = RadioField('Intent  Method:', choices=[
    ('rasa', 'Rasa Chatbot'),
    ('transformer_mode', 'Transformer Model')
],  default='rasa', validators=[Optional()])
    #submit = SubmitField('Submit')


    # Hidden Field to keep track of the platform
    basic_display_options = RadioField('Select Display Option', choices=[
        ('text', 'Text'),
        ('pie_chart', 'Pie Chart'),
        ('gauge', 'Gauge'),
        ('word_cloud', 'Word Cloud'),
        ('all', 'Show All'),
        ('Table_form', 'Table Form: Only valid for Mock data analysis')
    ], default='text')

    advanced_display_options = RadioField('Select Display Options', choices=[
        ('text_table', 'Text and Table'),
        ('bar_chart', 'Bar Chart'),
        ('radar_chart', 'Radar Chart'),
        ('word_cloud', 'Word Cloud'),
        ('show_all', 'Show All')
    ], default='text_table')

# Define both Submit Buttons
    submit_analyze = SubmitField('Submit')  # For regular analysis
    #Start Trend Analysis button (only shown if "Sentiment Trend Analysis" is selected)
    #go_to_trend_analysis = SubmitField('Go To Trend Analysis')  # Trigger the Trend Analysis


##########################################

class IntentClassificationForm(FlaskForm):
    intent_classification_type = RadioField(
        'Intent  Method:',
        choices=[
        ('rasa', ' Chatbot Mode 💬'), 
        ('transformer_mode', 'Transformer Mode')],
        validators=[DataRequired()]
    )


##########################################
    
class CRMContactForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone')

    submit = SubmitField('Create CRM Contact')

##########################################

class CRMDealForm(FlaskForm):
    dealname = StringField('Deal Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired()])
    dealstage = SelectField('Deal Stage', choices=[
        ('appointmentscheduled', 'Appointment Scheduled'),
        ('qualifiedtobuy', 'Qualified to Buy'),
        ('contractsent', 'Contract Sent')
    ], validators=[DataRequired()])
    associatedcontacts = SelectMultipleField('Associated Contacts', coerce=int)
    submit = SubmitField('Create Deal')

##########################################

class ChatForm(FlaskForm):
    message_content = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

##########################################
    
class TrendAnalysisForm(FlaskForm):
    trend_analysis_type = SelectField('Trend Analysis Type', choices=[
        ('generic', 'Generic Trend Analysis'),
        ('chat_messages', 'Chat Messages Trend Analysis'),
        ('aspect_based', 'Aspect-Based Trend Analysis')
        ],  default='generic', validators=[DataRequired()])
    start_date = DateField('Start Date    ', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    aspect = StringField('Aspect for ABSA Analysis', validators=[Optional()])
    user_id = IntegerField('User ID', validators=[Optional()])
    session_id = StringField('Session ID', validators=[Optional()])
    trend_time_scale = SelectField('Time Scale', choices=[
        ('none', 'None'),
        ('daily', 'Daily'), 
        ('weekly', 'Weekly'), 
        ('monthly', 'Monthly'), (
        'quarterly', 'Quarterly'), 
        ('yearly', 'Yearly')
    ], validators=[Optional()]) 

    trend_analysis_mode= SelectField('Time Scale', choices=[
        ('sentiment', 'Sentiment'),
        ('emotion', 'Emotion')
    ], validators=[Optional()])
      # Social Media Platform Selection
    file_data = RadioField('File Data', choices=[
        ('file', 'File(s)'),
        ('large_text', 'Large Text')
    ], validators=[Optional()]
    )

    file_upload = FileField('Upload Dataset (PDF, CSV or TXT)', validators=[Optional()], render_kw={'multiple': True, 'id': 'file-upload'})
    large_text = TextAreaField('Paste Large Text Here', validators=[Optional()])


    platform = RadioField('Social Media Platform', choices=[
        ('twitter', 'Twitter/X'),
        ('youtube', 'YouTube'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram')
    ], validators=[Optional()]
    )

    # Twitter Sub-fields
    twitter_handle = StringField('Twitter Handle or Hashtag', validators=[Optional()])
    twitter_url = URLField('Tweet URL', validators=[Optional()])
    twitter_Mock_text = TextAreaField('Tweet Mock Text', validators=[Optional()])

    # YouTube Sub-fields
    youtube_channel = StringField('YouTube Channel Name', validators=[Optional()])
    youtube_video = URLField('YouTube Video URL', validators=[Optional()])
    youtube_Mock_channel = StringField('YouTube Mock Channel ', validators=[Optional()])


    # Facebook Sub-fields
    facebook_page = StringField('Facebook Page Name', validators=[Optional()])
    facebook_post = URLField('Facebook Post URL', validators=[Optional()])

    # Instagram Sub-fields
    instagram_account = StringField('Instagram Username', validators=[Optional()])
    instagram_post = URLField('Instagram Post URL', validators=[Optional()])


    trend_display_options = RadioField('Select Display Options', choices=[
        ('text_table', 'Text and Table'),
        ('bar_chart', 'Bar Chart'),
        ('show_all', 'Show All')
    ], default='show_all')

    submit = SubmitField('Start Trend Analysis')

##########################################   