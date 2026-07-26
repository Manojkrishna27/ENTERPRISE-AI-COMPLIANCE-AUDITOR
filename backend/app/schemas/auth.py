from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    department_id: str | None = None
    role: str | None = "Viewer"


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
    description: str | None = ""
