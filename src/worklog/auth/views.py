from fastapi import APIRouter, Depends, HTTPException, Response
from .service import UserService
from .schemas import *
from src.worklog.config.auth import auth
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.db.core import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["🔑AUTH - access-portal"])

@router.post("/login", response_model=UserRead)
async def login(user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.authenticate_user(phone=user.phone, password=user.password)
    access_token, refresh_token, csrf_token = auth.create_tokens(
        user.id, 
        additional_data={
            "is_superuser": str(user.is_superuser), 
            "role": str(user.role),
            }
        )
    auth.set_tokens_in_cookies(response, access_token, refresh_token, csrf_token)   
    return user

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.create_user(user)
    return user

@router.get("/get-me", response_model=UserRead)
async def get_me(user_data = Depends(auth.get_user_data_dependency()), db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_profile(int(user_data['sub']))
    return user

