from fastapi import APIRouter, Depends
from .schemas import *
from .service import *
from src.worklog.db.core import get_db
from src.worklog.config.auth import auth

router = APIRouter(prefix="/api/v1/reshifts", tags=["RESHIFT"])

@router.post('/new/report/by/ai')
async def new_report_reshift(data: ReshiftCreate, db: AsyncSession = Depends(get_db)):
    service = ReShiftService(db)
    data = await service.create_report_reshift(data)
    return data

@router.get('/my', response_model=ReportListResponse)
async def my_report(db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    service = ReShiftService(db)
    data = await service.get_user_reports(user_id=int(current_user['sub']))
    return data

@router.post('/register/user/shift')
async def register_user_shift(data: CreateUserShifts, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    service = ReShiftService(db)
    data = await service.create_user_shifts(data)
    return data

@router.get('/get/user/shift')
async def get_user_shift(user_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    service = ReShiftService(db)
    data = await service.get_user_shifts(user_id=user_id)
    return data