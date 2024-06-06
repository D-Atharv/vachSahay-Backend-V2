from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .models import User, Token
from .mongodb import get_database
from .jwt import create_access_token, verify_access_token

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/register")
async def register(user: User):
    db = get_database()
    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    user.hash_password()
    db.users.insert_one(user.dict())
    return {"message": "User created successfully"}


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    user = db.users.find_one({"email": form.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    if not user.verify_password(form.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )
    return payload.get("sub")
