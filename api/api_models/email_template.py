from pydantic import BaseModel


class EmailTemplateCreate(BaseModel):
    template_name: str
    html_content: str


class EmailTemplateResponse(BaseModel):
    id: int
    template_name: str
    html_content: str

    class Config:
        orm_mode = True
