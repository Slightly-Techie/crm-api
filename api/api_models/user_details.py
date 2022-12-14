from pydantic import BaseModel,Field
from typing import Optional


class UserDetails(BaseModel):
    github_profile: str=Field('')
    twitter_profile: str=Field('')
    linkedin_profile: str=Field('')
    portfolio_url: Optional[str]=Field('')
    profile_pic_url: str=Field('')

    class config:
        orm_mode = True
