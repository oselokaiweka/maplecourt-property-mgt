import base64
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart 

from src.utils.credentials import get_google_credentials


def send_email(subject, sender, recipient, body):
    """
    Function sends email based on the provided parameters through
    organizations email account. 

    Args:
        subject (str): Email subject,
        sender (str): Sender email address,
        recipient (str): Recipient email address,
        body (str): Single or multi-line text.

    Returns:
      Either True or False (Boolean): If email is sent successfully it returns True, else it returns Fales. 
    """    
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.attach(MIMEText(body, "Plain"))

    service = get_google_credentials()

    try:
        create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()

        return True
    
    except Exception as e:
        print(e)

        return False
    


def read_email(sender, start_date, stop_date, subject):
    """
        Function accesses registered email using valid app credentials registered 
        on gcp account and retrieves emails based on specified arguements.

    Args:
        sender (str): sender title
        start_date (date str): date from which retrieval begins
        stop_date (date str): date from which retrieval ends
        subject (str): email subject

    Returns:
        email_data (list of dictionaries): Contains email subject and body in form of: 
        [{'subject':subject, 'body':email_body},] 
    """    

    service = get_google_credentials()

    try:
        print('Retrieving email(s)')
        query = f"from:{sender} after:{start_date} before:{stop_date} subject:{subject}"
        result = service.users().messages().list(userId='me',q=query).execute()
        messages = result.get('messages')
        
        if messages:
            
            email_data = []

            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg['payload']
                headers = payload['headers']
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None).split()

                if 'parts' in payload:
                    data = next((part['body']['data'] for part in payload['parts'] if 'data' in part['body']), None)
                elif 'data' in payload['body']:
                    data = payload['body']['data']
                else:
                    continue # Skip this message if it doesn't have bas64-encoded data
                try:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    soup = BeautifulSoup(body, 'html.parser')
                    email_body = soup.get_text(separator=' ').strip().split()

                    email_data.append({'subject':subject, 'email_body':email_body})
                except Exception as e:
                    print(f"Error processing email with subject: {subject}, error: {e}")

        return email_data
    
    except HttpError as e:
        print(f"Error while connecting to gmail: {e}")
    
    except Exception as e:
        print(f"Error while reading email: {e}")




    
