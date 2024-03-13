from pydantic import BaseModel
from enum import Enum

from utils.enums import EmailTemplateName


class EmailTemplateCreate(BaseModel):
    template_name: EmailTemplateName
    subject: str
    html_content: str


class EmailTemplateResponse(BaseModel):
    id: int
    template_name: str
    subject: str
    html_content: str

    class Config:
        from_attributes = True
