from fastapi import APIRouter, Depends, status
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page
from sqlalchemy.orm import Session

from api.api_models.email_template import EmailTemplateCreate, EmailTemplateResponse
from db.database import get_db
from db.repository.email_templates import EmailTemplateRepository
from services.email_template_service import EmailTemplateService
from utils.permissions import is_admin

email_templates_route = APIRouter(tags=["Email Templates"], prefix="/email-templates")


def _service(db: Session) -> EmailTemplateService:
    return EmailTemplateService(EmailTemplateRepository(db))


@email_templates_route.post("/", response_model=EmailTemplateResponse,
                            status_code=status.HTTP_201_CREATED)
def create_email_template(template: EmailTemplateCreate, db: Session = Depends(get_db),
                          current_user=Depends(is_admin)):
    return _service(db).create(template.template_name, template.subject, template.html_content)


@email_templates_route.get("/{template_id}", response_model=EmailTemplateResponse)
def read_email_template(template_id: int, db: Session = Depends(get_db)):
    return _service(db).get_by_id(template_id)


@email_templates_route.get("/", response_model=Page[EmailTemplateResponse])
def read_all_email_templates(db: Session = Depends(get_db)):
    return paginate(db, _service(db).get_all_query())


@email_templates_route.put("/{template_id}", response_model=EmailTemplateResponse)
def update_email_template(template_id: int, template_update: EmailTemplateCreate,
                          db: Session = Depends(get_db), current_user=Depends(is_admin)):
    return _service(db).update(template_id, template_update.model_dump())


@email_templates_route.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(template_id: int, db: Session = Depends(get_db),
                          current_user=Depends(is_admin)):
    _service(db).delete(template_id)
