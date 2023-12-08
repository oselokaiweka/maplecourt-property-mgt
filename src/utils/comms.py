import base64
from googleapiclient.discovery import build
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart 


def send_email(subject, sender, recipient, body, credentials):
    """
        Function sends email based on the provided parameters through
        organizations email account. 

    Args:
        subject (str): Email subject,
        sender (str): Sender email address,
        recipient (str): Recipient email address,
        body (str): Single or multi-line text, 
        credentials (Variable): Returned from the imported get_google_credentials() function.

    Returns:
        _type_: _description_
    """    
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.attach(MIMEText(body, "Plain"))

    try:
        service = build("gmail", "v1", credentials=credentials)
        create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return True
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False
