from pydantic import BaseModel,Field
from typing import Optional


class User_details(BaseModel):
    github_profile: str=Field(...)
    twitter_profile: str=Field(...)
    linkedin_profile: str=Field(...)
    portfolio_url: str=Field(...)
    profile_pic_url: str=Field(...)

