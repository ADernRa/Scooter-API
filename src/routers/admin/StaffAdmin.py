from src.dependencies import verify_admin
from fastapi import  Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models import Station, Staff, User

from src.schemas.StaffSchemas import (
    StaffCreate, StaffUpdate, StaffResponse
)

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admins"],
    dependencies=[Depends(verify_admin)]  
)
# Створити нового співробітника
@admin_router.post("station/{station_id}/staff", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def create_staff(station_id: int, staff: StaffCreate, db: AsyncSession = Depends(get_db)):
    query = select(Station).where(Station.id == station_id)
    result = await db.execute(query)
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

    if staff.user_id is not None:
            user = await db.execute(select(User).where(User.id == staff.user_id))
            if not user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with ID {staff.user_id} does not exist"
                )
        
    new_staff = Staff(**staff.model_dump(), station_id=station_id)
    db.add(new_staff)
    await db.commit()
    await db.refresh(new_staff)
    return new_staff

# Отримати список всіх співробітників на станції
@admin_router.get("station/{station_id}/staff", response_model=List[StaffResponse], status_code=status.HTTP_201_CREATED)
async def get_staff(station_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Staff).where(Staff.station_id == station_id)
    result = await db.execute(query)
    staff = result.scalars().all()
    return staff

# Оновити інформацію про співробітника
@admin_router.patch("station/{station_id}/staff/{staff_id}", response_model=StaffResponse)
async def update_staff(station_id: int, staff_id: int, staff_data: StaffUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Staff).where(Staff.id == staff_id)
    result = await db.execute(query)
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")

    if staff_data.station_id is not None:
        station = await db.execute(select(Station).where(Station.id == staff_data.station_id))
        if not station.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"It is not possible to lock the scooter. Stations with ID {staff_data.station_id} does not exist"
            )

    update_dict = staff_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
            setattr(staff, key, value)
    
    await db.commit()
    await db.refresh(staff)
    return staff

# Видалити запис про співробітника
@admin_router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff(
    staff_id: int, 
    db: AsyncSession = Depends(get_db)
    ):
    query = select(Staff).where(Staff.id == staff_id)
    result = await db.execute(query)
    staff = result.scalar_one_or_none()

    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scooter not found")

    delete_query = delete(Staff).where(Staff.id == staff_id)
    await db.execute(delete_query)
    await db.commit()
    return None