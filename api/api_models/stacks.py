from pydantic import BaseModel, Field
from datetime import datetime


class Stacks(BaseModel):
	id: str = Field(...)
	name: str = Field(...)
	created_at: datetime = Field(...)
	updated_at: datetime = Field(...)


	class Config:
		orm_mode = True


class StackCreate(BaseModel):
	name: str = Field(...)



