# email_assistant_task
This is my repository which contains my Personalized ai email assistant project.


The main focus of this project was to create a personalized email assistant which reads the mail , understands it and generate a response  while using web search , sending the message to slack and creating an event in the calender.

Step 1 - Connecting the gmail to imap server , Establishing a secure connection to Gmail's IMAP server , Logining to the Gmail account using email and app password
Step 2 - Creating a sqlite database for storing all the emails information.
Step 3 - Saving emails to the sqlite database.
Step 4 - Fetching the emails from the inbox and parsing them.(selecting the inbox folder to interact with the emails , searching for all emails without using any parameters , Processing the most recent emails , Fetching the full email data using the RFC822 format , Parsing the email content using the email library ,Decoding the email subject, sender's email address , Parsing the email timestamp (Date) , Extracting the body of the email and saving email data to the database)
Step 5 - Parsing the email's timestamp and returning it in a formatted string.
Step 6 - Extracting the body of the email , If the email isn't multipart (doesn't contains any attachments), it will just extract the plain text
Step 7 -  Saving the attachments(if any)
Step 8 - Main execution flow
Step 9 - Loading the hugging face models for text classification and generation
Step 10 - Classifying the email intent , Performing zero-shot classification , Printing the top predicted intent label
Step 11 - Generating a reply based on the email intent
Step 12 - Performing web search
Step 13 - Function to extract and summarize relevant parts of the search results.
Step 14 - If search results are found, extract the summary and use it in the response
Step 15 - Creating the event in google calender.
Step 16 - Sending the email using smtp server.
Step 17 - Sending the message on slack.


