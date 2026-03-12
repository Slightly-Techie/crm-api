from fastapi import HTTPException, status

from db.repository.email_templates import EmailTemplateRepository
from db.models.email_template import EmailTemplate


class EmailTemplateService:
    def __init__(self, template_repo: EmailTemplateRepository):
        self.template_repo = template_repo

    def create(self, template_name: str, subject: str, html_content: str) -> EmailTemplate:
        return self.template_repo.create(template_name, subject, html_content)

    def get_by_id(self, template_id: int) -> EmailTemplate:
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email template not found")
        return template

    def get_all_query(self):
        return self.template_repo.get_all_paginated_query()

    def update(self, template_id: int, update_data: dict) -> EmailTemplate:
        template = self.get_by_id(template_id)
        return self.template_repo.update(template, update_data)

    def delete(self, template_id: int) -> None:
        template = self.get_by_id(template_id)
        self.template_repo.delete_obj(template)
