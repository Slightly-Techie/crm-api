import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
from starlette.responses import JSONResponse
from core.config import settings


def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


async def send_email(email: str, reset_token: str, url: str, username: str) -> JSONResponse:
    """
    Click on manage google account
    Go to Security
    Enable Two-Step Verification(how to sign in with google)
    Create an App Password
    Generate an App Password
    """
    email_sender = settings.EMAIL_SENDER
    email_password = settings.EMAIL_PASSWORD
    email_receiver = f'{email}'
    reset_password_url = f"{url}{settings.URL_PATH}?{urlencode({'token': reset_token})}"

    subject = "Reset Password"
    html = read_html_file('utils/password-reset.html')
    html = html.format(username, reset_password_url)
    
    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    html_part = MIMEText(html, 'html')
    em.attach(html_part)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(settings.EMAIL_SERVER, settings.EMAIL_PORT, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
