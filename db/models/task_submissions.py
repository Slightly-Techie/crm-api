from sqlalchemy import Column, Integer, String, ForeignKey

class TaskSubmission(Base):
    __tablename__ = "task_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    github_link = Column(String, nullable=False)
    live_demo_url = Column(String, nullable=True)
    additional_info = Column(String, nullable=True)