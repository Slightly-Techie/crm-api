import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
from starlette.responses import JSONResponse
from core.config import settings

async def send_email(email: str, reset_token: str) -> JSONResponse:
    """
    Click on manage google account
    Go to Security
    Enable Two-Step Verification(how to sign in with google)
    Create an App Password
    Generate an App Password
    """
    email_sender = 'your-email@gmail.com'
    email_password = 'app password not gmail password'
    email_receiver = f'{email}'
    reset_password_url = f"{settings.BASE_URL}reset-password?{urlencode({'token': reset_token})}"

    subject = "Reset Password"
    html = f"""\
                <html>
                    <body>
                        <p>Click on this link to reset your password:</p>
                        <p><a href="{reset_password_url}">{reset_password_url}</a></p>
                    </body>
                </html>
            """

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
