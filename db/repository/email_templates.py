from typing import Optional

from sqlalchemy import select

from db.models.email_template import EmailTemplate
from db.repository.base import BaseRepository


class EmailTemplateRepository(BaseRepository):
    model = EmailTemplate

    def get_by_name(self, template_name: str) -> Optional[EmailTemplate]:
        return self.db.query(EmailTemplate).filter(
            EmailTemplate.template_name == template_name
        ).first()

    def create(self, template_name: str, subject: str, html_content: str) -> EmailTemplate:
        template = EmailTemplate(
            template_name=template_name,
            subject=subject,
            html_content=html_content
        )
        return self.save(template)

    def update(self, template: EmailTemplate, update_data: dict) -> EmailTemplate:
        for key, value in update_data.items():
            setattr(template, key, value)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_all_paginated_query(self):
        return select(EmailTemplate).order_by(EmailTemplate.template_name)
