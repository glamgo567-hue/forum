from datetime import datetime

from pydantic import BaseModel, EmailStr, model_validator


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self

class UserRead(BaseModel):
    username: str
    email: EmailStr
    reputation: int
    created_at: datetime

    model_config={"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"