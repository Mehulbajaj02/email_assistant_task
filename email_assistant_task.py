import imaplib
import email
from email.header import decode_header

# Connecting the gmail to imap server
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "mehulbajaj0202@gmail.com"
APP_PASSWORD = "znoe nqzx wuaq fnnv"

def connect_to_gmail():
    """Connect to Gmail using IMAP and return the connection object."""
    try:
        # Establish a secure connection to Gmail's IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

        # Login to the Gmail account using email and app password
        mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
        print("Successfully connected to Gmail")
        return mail
    except Exception as e:
        print(f"Failed to connect to Gmail: {str(e)}")
        return None

# Creating a sqlite database for storing all the emails information.

import sqlite3

def create_db():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                        email_id TEXT PRIMARY KEY,
                        sender TEXT,
                        subject TEXT,
                        body TEXT,
                        date_received TEXT)''')
    conn.commit()
    conn.close()

# Saving emails to the sqlite database.

def save_email_to_db(email_data):
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT OR REPLACE INTO emails (email_id, sender, subject, body, date_received)
                      VALUES (?, ?, ?, ?, ?)''', email_data)

    conn.commit()
    conn.close()


# Fetching the emails from the inbox and parsing them.
def fetch_emails(mail):

    try:

        mail.select("inbox") #selecting the inbox folder to interact with the emails.
        status, messages = mail.search(None, 'ALL')  # searching for all emails without using any parameters
        email_ids = messages[0].split() # Convert messages to a list of email IDs

# Processing the most recent emails.
        for email_id in email_ids[-1:]:
            status, msg_data = mail.fetch(email_id, "(RFC822)")  # Fetching the full email data using the RFC822 format.
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parsing the email content using the email library
                    msg = email.message_from_bytes(response_part[1])

                     # Decoding the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    # Decoding the sender's email address
                    from_ = msg.get("From")

                    # Parsing the email timestamp (Date)
                    date_received = msg.get("Date")
                    timestamp = parse_timestamp(date_received)

                    print(f"From: {from_}")
                    print(f"Subject: {subject}")
                    print(f"Date: {timestamp}")

                    # Extracting the body of the email
                    body = extract_body(msg)

                    # Printing out the body content
                    print(f"Body: {body}")
                    print("=" * 50)  # Separator between emails

                    # Saving email data to the database
                    save_email_to_db((email_id.decode(), from_, subject, body, timestamp))

    except Exception as e:
        print(f"Failed to fetch emails: {str(e)}")

# Parsing the email's timestamp and returning it in a formatted string.

from email.utils import parsedate_tz, mktime_tz

def parse_timestamp(date_received):

    try:
        # Converting the Date header into a datetime object and returning the formatted string
        timestamp = parsedate_tz(date_received)
        if timestamp:
            return str(mktime_tz(timestamp))
    except Exception as e:
        print(f"Failed to parse timestamp: {str(e)}")
        return None


# Extracting the body of the email
def extract_body(msg):

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" in content_disposition:
                # Handling attachment here (saving or processing)
                filename = part.get_filename()
                if filename:
                    print(f"Saving attachment: {filename}")
                    save_attachment(part)
            elif content_type == "text/plain":
                # Extract plain text body
                body += part.get_payload(decode=True).decode()
            elif content_type == "text/html":
                # Extract HTML body (optional)
                body += part.get_payload(decode=True).decode()
    else:
        # If the email isn't multipart (doesn't contains any attachments), it will just extract the plain text
        body = msg.get_payload(decode=True).decode()

    return body


# Saving the attachments(if any)
import os
def save_attachment(part):
    """Save email attachments to the local filesystem."""
    filename = part.get_filename()
    if filename:
        # Save the file to disk
        if not os.path.exists("attachments"):
            os.makedirs("attachments")
        filepath = os.path.join("attachments", filename)
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))
        print(f"Attachment saved as: {filepath}")


# Main execution flow
if __name__ == "__main__":
    create_db()  # Run this once to create the database
    mail = connect_to_gmail()
    if mail:
        fetch_emails(mail)
        mail.logout()  # Logout after processing

from transformers import pipeline
# Loading the hugging face models for text classification and generation (mention the exact model.)

classifier = pipeline("zero-shot-classification" , model = "facebook/bart-large-mnli")  # For intent detection
generator = pipeline("text-generation", model="gpt2")  # For generating replies


# # Classify the email intent
email_text = "I need to file a complaint regarding my recent order."

# candidate_labels = ["Request", "Complaint", "General Inquiry", "Question"]
# intent_result = classifier(email_text, candidate_labels)
# print("Intent:", intent_result["label"])  # It returns the predicted intent label

candidate_labels = [
    "Request",  # For emails asking for something
    "Inquiry",  # For emails asking for information
    "Complaint",  # For emails expressing dissatisfaction
    "Thank You",  # For emails expressing gratitude
    "Follow-up",  # For emails checking in on previous topics
    "Confirmation",  # For emails confirming something
    "Scheduling",  # For emails related to meetings or events
    "General Inquiry"  # For open-ended questions
]

# Performing zero-shot classification
intent_result = classifier(email_text, candidate_labels)

# Print the top predicted intent label
print("Predicted Intent:", intent_result['labels'][0])  # 'labels' contains the list of predicted labels

# Generate a reply based on the email intent
reply_prompt = "The employee wants to know about the complaint confirmation of the discount."
generated_reply = generator(reply_prompt, max_length=300)

print("Generated Reply:", generated_reply[0]['generated_text'])


# Performing web search
import requests

# Function to perform web search using Google Custom Search API
def perform_web_search(query, api_key, search_engine_id):
    # Google Custom Search API URL
    url = "https://www.googleapis.com/customsearch/v1"
    
    # Parameters for the search query
    params = {
        'q': query,  # The search query
        'key': api_key,  # Your API key
        'cx': search_engine_id,  # Custom search engine ID
        'num': 3  # Number of results to retrieve
    }
    
    # Send GET request to Google API
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print("Error with web search request:", response.status_code)
        return None

# Example usage
api_key = 'AIzaSyD8TVtwEeONmSx2OvJGHfELbBzDssJ4_hE'
search_engine_id = '14b6e8b3582464982'
query = "What are the benefits of AI in healthcare?"

search_results = perform_web_search(query, api_key, search_engine_id)

if search_results:
    # Extract and print the top results
    for i, item in enumerate(search_results['items']):
        print(f"Result {i+1}:")
        print(f"Title: {item['title']}")
        print(f"Link: {item['link']}")
        print(f"Snippet: {item['snippet']}")
        print("-" * 50)


# Function to extract and summarize relevant parts of the search results
def extract_summary(search_results):
    summaries = []
    
    for item in search_results['items']:
        title = item['title']
        link = item['link']
        snippet = item['snippet']
        
        summary = f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n"
        summaries.append(summary)
    
    # Combine all summaries into one string
    return "\n".join(summaries)

# Example usage
if search_results:
    reply_summary = extract_summary(search_results)
    print("Summary of the web search results:\n")
    print(reply_summary)


def generate_email_reply(email_content, search_results):
    # If search results are found, extract the summary and use it in the response
    if search_results:
        reply_summary = extract_summary(search_results)
        response = f"Hello,\n\nI found some relevant information for your query:\n\n{reply_summary}\n\nBest regards,\nYour AI Assistant"
    else:
        response = "Sorry, I couldn't find relevant information for your query. Please try again later."
    
    return response

# Example email content and response generation
email_content = "Can you explain the benefits of AI in healthcare?"
search_results = perform_web_search(email_content, api_key, search_engine_id)

email_reply = generate_email_reply(email_content, search_results)
print("Generated Email Reply:\n")
print(email_reply)


import base64

def get_emails():
    creds = authenticate_google()
    service = build('gmail', 'v1', credentials=creds)

    # Get the list of emails with "meeting" in the subject
    results = service.users().messages().list(userId='me', q="subject:meeting").execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            payload = msg['payload']
            headers = payload['headers']

            # Extract email subject and body
            subject = next((item['value'] for item in headers if item['name'] == 'Subject'), '')
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            # Extract meeting info from the subject or body using regex or NLP
            extract_meeting_info(subject, body)

import re

def extract_meeting_info(subject, body):
    meeting_details = {}

    # Example: Extract date and time using regex patterns
    date_pattern = r'(\d{4}-\d{2}-\d{2})'  # Match dates in the format YYYY-MM-DD
    time_pattern = r'(\d{2}:\d{2})'  # Match time in the format HH:MM (24-hour format)

    date_match = re.search(date_pattern, body)
    time_match = re.search(time_pattern, body)

    if date_match and time_match:
        meeting_details['date'] = date_match.group(1)
        meeting_details['time'] = time_match.group(1)

    # Extract the meeting title (optional, could use the subject)
    meeting_details['title'] = subject

    if meeting_details:
        # Format the start time and end time (adding 1 hour to the meeting)
        start_time = f"{meeting_details['date']}T{meeting_details['time']}:00"
        end_time = f"{meeting_details['date']}T{int(meeting_details['time'][:2]) + 1}{meeting_details['time'][2:]}:00"
        
        create_calendar_event(meeting_details['title'], start_time, end_time)

import dateparser

def extract_meeting_info(subject, body):
    meeting_details = {}

    # Extract the date and time using dateparser (it supports natural language parsing)
    date_time = dateparser.parse(body)  # Automatically extracts date and time from the email body

    if date_time:
        meeting_details['date'] = date_time.date()
        meeting_details['time'] = date_time.time()

    # Extract the meeting title (optional)
    meeting_details['title'] = subject

    if meeting_details:
        # Format the start time and end time
        start_time = f"{meeting_details['date']}T{meeting_details['time']}:00"
        end_time = f"{meeting_details['date']}T{int(meeting_details['time'][:2]) + 1}{meeting_details['time'][2:]}:00"
        
        create_calendar_event(meeting_details['title'], start_time, end_time)
def create_calendar_event(summary, start_time, end_time):
    creds = authenticate_google()  # Ensure the user is authenticated
    service = build('calendar', 'v3', credentials=creds)

    # Event details
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/kolkata',  # Change to your timezone
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/kolkata',  # Change to your timezone
        },
    }

    # Insert event into Google Calendar
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {created_event.get('htmlLink')}")
    return created_event

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Function to perform web search using Google Custom Search API
def perform_web_search(query, api_key, search_engine_id):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': search_engine_id,
        'num': 3  # Number of results to retrieve
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        print("Error with web search request:", response.status_code)
        return None

# Function to extract and summarize relevant parts of the search results
def extract_summary(search_results):
    summaries = []
    for item in search_results['items']:
        title = item['title']
        link = item['link']
        snippet = item['snippet']
        summary = f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n"
        summaries.append(summary)
    return "\n".join(summaries)

# Function to generate the email reply based on the content and search results
def generate_email_reply(email_content, search_results=None):
    # Start the base automated reply
    base_reply = "Hello,\n\nThank you for your email. Here's my reply:\n\n"
    
    # Case 1: If web search results are available
    if search_results:
        reply_summary = extract_summary(search_results)
        full_reply = f"{base_reply}I found some additional information for you:\n\n{reply_summary}\n\nBest regards,\nYour AI Assistant"
    
    # Case 2: If no web search was needed (normal AI-generated reply)
    else:
        full_reply = f"{base_reply}Here's the information I can provide based on your query:\n\n[Automated AI Response Here]\n\nBest regards,\nYour AI Assistant"
    
    return full_reply

# Function to send the email via SMTP
def send_email(subject, body, to_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'mehulbajaj0202@gmail.com'
    sender_password = 'znoe nqzx wuaq fnnv'

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email using SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        print("Email sent successfully!")

# Example: Handling an incoming email and sending the appropriate response
email_content = "emails.db"
api_key = 'AIzaSyD8TVtwEeONmSx2OvJGHfELbBzDssJ4_hE'
search_engine_id = '14b6e8b3582464982'

# Perform web search if needed
search_results = perform_web_search(email_content, api_key, search_engine_id)

# Generate the email reply based on the search results
email_reply = generate_email_reply(email_content, search_results)

# Send the email reply to the recipient
send_email("AI-Powered Email Reply", email_reply, "9873286383bajaj@gmail.com")


from slack_sdk import WebClient

SLACK_TOKEN = 'xoxb-8697026482323-8685351576887-a4DHCyFfOFVjPdCn68tUjLlV'

client = WebClient(token=SLACK_TOKEN)

def send_slack_message(channel, message):
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        if response["ok"]:
            print(f"Message sent to {channel}")
        else:
            print(f"Error: {response['error']}")
    except Exception as e:
        print(f"An error occurred: {e}")

send_slack_message("D08L5ABH2DD", "Hello, world!")
