from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    department_id: Optional[str] = None
    role: Optional[str] = "Viewer"

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    token: str
    password: str

class VerifyEmailSchema(BaseModel):
    token: str

class UserRoleUpdateSchema(BaseModel):
    role: str

class DepartmentCreateSchema(BaseModel):
    name: str
    description: Optional[str] = ""
