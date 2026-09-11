from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.models import User
from src.schemas.UserSchemas import (UserCreate, UserResponse, Token) 
from src.services import (security, auth)
from src.database import engine, get_db


router = APIRouter(
    prefix="/api/v1/authorization", 
    tags=["auth"]
    )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate, 
    db: AsyncSession = Depends(get_db)):

    query = select(User).where(User.login == user_data.login)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Login already registered")
    
    hashed_pwd = security.get_password_hash(user_data.password)
    
    new_user = User(login=user_data.login, hashed_password=hashed_pwd)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)):

    query = select(User).where(User.login == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user.login})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user