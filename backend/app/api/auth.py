from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, hash_password, verify_password
from app.schema.auth import TokenResponse, UserRegisterRequest
from app.shared.dependencies import get_db
from sqlalchemy.orm import Session
from app.model.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == request.username).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=request.username, password=hash_password(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token({"sub": str(new_user.id)})
    return TokenResponse(access_token=token, token_type="bearer")

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    
    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(db_user.id)})
    return TokenResponse(access_token=token, token_type="bearer")

@router.post("/logout")
def logout():
    return {"message": "Logout successful"}