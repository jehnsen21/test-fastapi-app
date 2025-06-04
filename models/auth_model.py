
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4

class Token(BaseModel):
    access_token: str
    token_type: str