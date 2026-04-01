import logging
import smtplib
import ssl
import anyio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlencode
from starlette.responses import JSONResponse

# from api.api_models.email_template import EmailTemplateName
from core.config import settings
# from db.models.email_template import EmailTemplate


logger = logging.getLogger(__name__)


def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


async def send_email(subject: str, recipient_email: str, html_content: str) -> JSONResponse:
    """
    Generic email sending function supporting both SMTP (port 587 with STARTTLS) and SMTP_SSL (port 465).
    """
    email_sender = settings.EMAIL_SENDER
    email_password = settings.EMAIL_PASSWORD
    email_receiver = recipient_email
    email_port = int(settings.EMAIL_PORT)

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    html_part = MIMEText(html_content, 'html')
    em.attach(html_part)

    context = ssl.create_default_context()

    def _send_email_sync() -> None:
        # Port 587 uses STARTTLS, port 465 uses SMTP_SSL
        if email_port == 465:
            with smtplib.SMTP_SSL(settings.EMAIL_SERVER, email_port, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
        else:  # Port 587 or other non-SSL ports
            with smtplib.SMTP(settings.EMAIL_SERVER, email_port, timeout=10) as smtp:
                smtp.starttls(context=context)
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())

    try:
        await anyio.to_thread.run_sync(_send_email_sync)
        
        return JSONResponse(status_code=200, content={"message": "Email sent successfully"})
    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed while sending email")
        return JSONResponse(status_code=500, content={"message": "Unable to send email at the moment."})
    except smtplib.SMTPException:
        logger.exception("SMTP error while sending email")
        return JSONResponse(status_code=500, content={"message": "Unable to send email at the moment."})
    except Exception:
        logger.exception("Unexpected error while sending email")
        return JSONResponse(status_code=500, content={"message": "Unable to send email at the moment."})


async def send_password_reset_email(email: str, reset_token: str, username: str, email_template):
    # subject = "Reset Password"
    reset_password_url = f"{settings.BASE_URL}{settings.URL_PATH}?{urlencode({'token': reset_token})}"

    if email_template:
        html_content = email_template.html_content.format(username, reset_password_url)
        email_subject = email_template.subject
    else:
        try:
            html_content = read_html_file(
                'utils/email_templates/password-reset.html'
                ).format(username, reset_password_url)
        except FileNotFoundError:
            html_content = f"Hello {username}, please reset your password by clicking this link: {reset_password_url}"
        email_subject = "Slightly Techie Password Reset"

    await send_email(email_subject, email, html_content)


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
        logger.warning("Task email template file not found; using fallback plain text")
        html_content = f"Hello {first_name}, Kindly work on this task and submit:\n {task}"
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
