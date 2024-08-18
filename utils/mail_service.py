import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
from starlette.responses import JSONResponse

from api.api_models.email_template import EmailTemplateName
from core.config import settings
from db.models.email_template import EmailTemplate
from sqlalchemy.orm import Session
from fastapi import Depends
from db.database import get_db


def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
async def send_email(subject: str, recipient_email: str, html_content: str) -> JSONResponse:
    """
    Generic email sending function.
    """
    email_sender = settings.EMAIL_SENDER
    email_password = settings.EMAIL_PASSWORD
    email_receiver = recipient_email

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    html_part = MIMEText(html_content, 'html')
    em.attach(html_part)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(settings.EMAIL_SERVER, settings.EMAIL_PORT, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})


async def send_password_reset_email(email: str, reset_token: str, username: str,db: Session = Depends(get_db)):
    subject = "Reset Password"
    reset_password_url = f"{settings.BASE_URL}{settings.URL_PATH}?{urlencode({'token': reset_token})}"

    email_template = db.query(EmailTemplate).filter(EmailTemplate.template_name == EmailTemplateName.password_reset).first()
    
    if email_template:
        html_content = email_template.html_content.format(username, reset_password_url)
    else:
        try:
            html_content = read_html_file('utils/email_templates/password-reset.html').format(username, reset_password_url)
        except FileNotFoundError:
            html_content = f"Hello {username}, please reset your password by clicking this link: {reset_password_url}"
    
    await send_email(email_template.subject, email, html_content)


async def send_applicant_task(
        email: str, first_name: str, task: str):
    """Send technical task to the applicant"""
    # email_sender = settings.EMAIL_SENDER
    # email_password = settings.EMAIL_PASSWORD
    # email_receiver = f'{email}'
    subject = "Invitation to Technical Challenge"
    try:
        html_content = read_html_file('utils/email_templates/task_template.html').format(first_name, task)
    except FileNotFoundError:
        print("File not found")
        html_content = f"Hello {first_name}, Kindly work on the this task and submit:\n {task}"
    # html = task.format(first_name)

    # em = MIMEMultipart()
    # em['From'] = email_sender
    # em['To'] = email_receiver
    # em['Subject'] = subject
    # html_part = MIMEText(html, 'html')
    # em.attach(html_part)

    # context = ssl.create_default_context()

    await send_email(subject, email, html_content)

    # with smtplib.SMTP_SSL(settings.EMAIL_SERVER, settings.EMAIL_PORT, context=context) as smtp:
    #     smtp.login(email_sender, email_password)
    #     smtp.sendmail(email_sender, email_receiver, em.as_string())
