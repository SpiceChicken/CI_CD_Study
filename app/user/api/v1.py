from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.security import verify_password, create_access_token

from app.user.crud import *
from app.user.schemas import *
from app.user.models import User

router = APIRouter()

@router.post("/signup", include_in_schema=False)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(db, user)
    token = create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": f"bearer {token}"}
