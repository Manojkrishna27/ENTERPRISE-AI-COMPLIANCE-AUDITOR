from pydantic import BaseModel
from typing import Optional

class PolicyUploadSchema(BaseModel):
    name: str
    description: Optional[str] = ""
    category: Optional[str] = "Custom"
