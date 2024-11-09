from pydantic import BaseModel
from pydantic.fields import Field


class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserAuth(BaseModel):
    id: int
    username: str
    email: str

class UserDisplay(BaseModel):
    username: str = Field(alias='Username')
    email: str = Field(alias='Email')
    class Config():
        from_attributes = True

class UserSignIn(BaseModel):
    username: str
    password: str