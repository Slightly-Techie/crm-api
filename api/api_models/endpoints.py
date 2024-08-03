from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class EndpointBase(BaseModel):
    endpoint: str
    status: Optional[bool] = False
