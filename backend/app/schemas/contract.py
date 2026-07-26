from pydantic import BaseModel


class ContractCreateSchema(BaseModel):
    name: str
    description: str | None = ""
    department_id: str | None = None
