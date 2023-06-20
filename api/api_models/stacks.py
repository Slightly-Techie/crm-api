from pydantic import BaseModel, Field


class Stacks(BaseModel):
	id: str = Field(...)
	name: str = Field(...)
	created_at: str = Field(...)
	updated_at: str = Field(...)


	class Config:
		orm_mode = True


class StackCreate(BaseModel):
	name: str = Field(...)



