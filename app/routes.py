from fastapi import APIRouter
from app.auth import register

router = APIRouter()

@router.post("/register")
@router.post("/login")
@app.post("/upload/")
