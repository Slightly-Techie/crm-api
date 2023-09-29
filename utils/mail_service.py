from typing import Tuple
from urllib.parse import urlencode
import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# Define your email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_FROM=os.environ.get("MAIL_FROM"),
    MAIL_PORT=os.environ.get("MAIL_PORT"),
    MAIL_SERVER=os.environ.get("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Setup mail service with MailChimp SMTP & API Credentials

async def send_email(email: str, reset_token: str) -> JSONResponse:
    reset_password_url = f"http://127.0.0.1:8080/reset-password?{urlencode({'token': reset_token})}"

    subject = "Reset Password"
    html = f"""\
                <html>
                    <body>
                        <p>Click on this link to reset your password:</p>
                        <p><a href="{reset_password_url}">{reset_password_url}</a></p>
                    </body>
                </html>
            """

    message = MessageSchema(
        subject=subject,
        recipients=[email], 
        body=html,
        subtype=MessageType.html
    )

    # Create a FastMail instance and send the email
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        return JSONResponse(status_code=200, content={"message": "Email has been sent"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to send email: {str(e)}"})
