from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.api_models.email_template import EmailTemplateCreate, EmailTemplateResponse
from db.database import get_db
from db.models.email_template import EmailTemplate
from utils.permissions import is_admin

email_templates_route = APIRouter(tags=["Email Templates"], prefix="/email-templates")


@email_templates_route.post("/", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_email_template(template: EmailTemplateCreate, db: Session = Depends(get_db), current_user=Depends(is_admin)):
    db_template = EmailTemplate(template_name=template.template_name,subject=template.subject, html_content=template.html_content)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@email_templates_route.get("/{template_id}", response_model=EmailTemplateResponse)
def read_email_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if db_template is None:
        raise HTTPException(status_code=404, detail="Email template not found")
    return db_template


@email_templates_route.put("/{template_id}", response_model=EmailTemplateResponse)
def update_email_template(template_id: int, template_update: EmailTemplateCreate, db: Session = Depends(get_db), current_user=Depends(is_admin)):
    db_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Email template not found")
    db_template.template_name = template_update.template_name
    db_template.html_content = template_update.html_content
    db.commit()
    db.refresh(db_template)
    return db_template

@email_templates_route.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(template_id: int, db: Session = Depends(get_db), current_user=Depends(is_admin)):
    db_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Email template not found")
    db.delete(db_template)
    db.commit()
    return {"message": "Email template deleted successfully"}
