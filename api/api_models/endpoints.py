from pydantic import BaseModel
from typing import Optional


class EndpointBase(BaseModel):
    endpoint: str
    status: Optional[bool] = False
