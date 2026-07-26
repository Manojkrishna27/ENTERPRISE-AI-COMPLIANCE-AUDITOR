from pydantic import BaseModel


class CopilotChatSchema(BaseModel):
    question: str
