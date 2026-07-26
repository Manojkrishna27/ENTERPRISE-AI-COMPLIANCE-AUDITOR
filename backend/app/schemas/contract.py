from pydantic import BaseModel
from typing import Optional, List, Any

class ContractCreateSchema(BaseModel):
    name: str
    description: Optional[str] = ""
    department_id: Optional[str] = None
