from typing import Tuple
import yagmail
from urllib.parse import urlencode

def send_reset_password_email(email: str, reset_token: str) -> Tuple[str, str]:
    sender_email = "user@example.com" # Set up env variables for your mail, and app password
    sender_password = "app_password" 

    reset_password_url = f"http://127.0.0.1:8080/reset-password?{urlencode({'token': reset_token})}"

    subject = "Reset Password"
    text = f"Click on this link to reset your password: {reset_password_url}"
    html = f"""\
                <html>
                    <body>
                        <p>Click on this link to reset your password:</p>
                        <p><a href="{reset_password_url}">{reset_password_url}</a></p>
                    </body>
                </html>
            """

    yag = yagmail.SMTP(sender_email, sender_password)
    
    contents = [text, html]
    
    yag.send(to=email, subject=subject, contents=contents)
    
    return "Reset password email sent successfully", email
