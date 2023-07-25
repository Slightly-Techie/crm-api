from typing import Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from typing import Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode

def send_reset_password_email(email: str, reset_token: str) -> Tuple[str, str]:
    sender_email = "user@example.com"
    sender_password = "your_password" 

    reset_password_url = f"http://127.0.0.1:8000/reset-password?{urlencode({'token': reset_token})}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset Password"
    message["From"] = sender_email
    message["To"] = email

    text = f"Click on this link to reset your password: {reset_password_url}"
    html = f"""\
    <html>
        <body>
            <p>Click on this link to reset your password:</p>
            <p><a href="{reset_password_url}">{reset_password_url}</a></p>
        </body>
    </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())

    return "Reset password email sent successfully", email
