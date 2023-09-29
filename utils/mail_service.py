from urllib.parse import urlencode
import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

# Define your email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("USERNAME", "AnyName"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "md-XnF_xUedhL_K8aQFqgnneQ"),
    MAIL_FROM=os.getenv("MAIL_FROM", "neilohene@gmail.com"),
    MAIL_PORT=os.getenv("MAIL_PORT", 587),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.mandrillapp.com"),
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
