from pydantic import BaseModel


class PolicyUploadSchema(BaseModel):
    name: str
    description: str | None = ""
    category: str | None = "Custom"
