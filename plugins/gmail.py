from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# import email.mime.text.MIMEText


import base64
from email.message import EmailMessage

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def create_email_with_attachment(recipient, subject, content, attachment_paths=None):
    # Create the MIMEMultipart object and set the headers
    message = MIMEMultipart()
    message['to'] = recipient
    message['from'] = 'milandin63@gmail.com'
    message['subject'] = subject

    # Attach the content
    message.attach(MIMEText(content, 'html'))

    # Attach the file, if provided
    if attachment_paths:
        for attachment_path in attachment_paths.split(","):
            with open(attachment_path, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {attachment_path}",
                )

                # Add attachment to message
                message.attach(part)

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}

# Usage:
# create_email_with_attachment(recipient, subject, content, "path/to/your/file.txt")

def send_email(subject, content, recipient, attachments=None):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """


    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        # message = EmailMessage()

        # message.set_content(content)
        # print(content)

        # message['To'] = recipient
        # message['From'] = 'milandin63@gmail.com'
        # message['Subject'] = subject

        # # encoded message
        # encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
        #     .decode()

        # create_message = {
        #     'raw': encoded_message
        # }

        # message = MIMEText(content, 'html')
        # message['to'] = recipient
        # message['from'] = 'milandin63@gmail.com'
        # message['subject'] = subject
        # create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
        # # create_message = {'raw': base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')}

        create_message = create_email_with_attachment(recipient, subject, content, attachments)



        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return "email sent"





if __name__ == '__main__':
    send_email('hello world', 'hello hello ello hell oello hell oello hello ello ello h elloe llo hell oello helloello ello helloello helloello helloello ello helloello helloello helloello', "milandin62@gmail.com")