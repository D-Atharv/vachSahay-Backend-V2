from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext


class User(BaseModel):
    email: EmailStr = Field()
    password: str = Field()
    first_name: str | None = None
    last_name: str | None = None
    nationality: str | None = None
    gender: str | None = None
    contact_number: str | None = None
    age: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
