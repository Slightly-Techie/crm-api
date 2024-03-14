from db.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, text


class EmailTemplate(Base):
    __tablename__ = 'email_templates'
    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String, unique=True, index=True)
    html_content = Column(String)
    subject = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))