from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.core.security import verify_password
from app.core.security import create_access_token

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}
@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }