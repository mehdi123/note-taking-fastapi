from pydantic import Field, EmailStr

from .core import IDModelMixin, CoreModel, BaseResponse

class User(CoreModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserLogin(CoreModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

class UserInDB(User, IDModelMixin):
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True

class UserToken(CoreModel, BaseResponse):
    token: str
    expires_in: int

class UserPasswordChange(CoreModel):
    new_password: str = Field(...)

class UserPayload(CoreModel):
    email: EmailStr