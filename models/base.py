# models/base.py
from pydantic import BaseModel
from datetime import datetime

class CustomBaseModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()  # Ensure datetime serialization
        }
        from_attributes = True  # Replaces orm_mode