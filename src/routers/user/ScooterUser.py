from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone
from sqlalchemy.orm import selectinload

from src.services.ride_service import calculate_cost
from src.database import get_db
from src.models import Scooter, Station, Ride
from src.models.RidesModel import StatusRide

from src.schemas.ScooterSchemas import (
    ScooterResponse, ScooterReturn
)

router = APIRouter(
    prefix="/api/v1/user", 
    tags=["users"]
    )


# Отримати інформацію про незайняті самокати
@router.get("/{station_id}/scooters/available", response_model=List[ScooterResponse])
async def get_avaible_scooter(station_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Scooter).where(Scooter.station_id == station_id, Scooter.is_available == True)
    result = await db.execute(query)
    scooters = result.scalars().all()
    print(scooters)
    return scooters

# Арендувати самокат
@router.patch("/{station_id}/scooters/{scooter_id}/rent", response_model=ScooterResponse)
async def rent_scooter(station_id: int, scooter_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Station).where(Station.id == station_id)
    result = await db.execute(query)
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
    
    query = select(Scooter).where(Scooter.id == scooter_id, Scooter.station_id == station_id) 
    result = await db.execute(query)
    scooter = result.scalar_one_or_none()

    if not scooter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scooter not found")

    if not scooter.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scooter is not available")

    new_ride = Ride(
        scooter_id = scooter_id,
        start_ride = datetime.now(),
        status = StatusRide.ACTIVE,
        cost = 0.0
    )

    scooter.is_available = False

    db.add(new_ride)
    await db.commit()
    await db.refresh(scooter)
    await db.refresh(new_ride)
    return scooter

# Припинити аренду самокату
@router.patch("/{station_id}/scooters/{scooter_id}/return", response_model=ScooterResponse)
async def return_scooter(station_id: int, scooter_id: int, return_data: ScooterReturn, db: AsyncSession = Depends(get_db)):

    query = select(Scooter).where(Scooter.id == scooter_id, Scooter.station_id == station_id) 
    result = await db.execute(query)
    scooter = result.scalar_one_or_none()

    if not scooter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scooter not found")

    if scooter.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scooter is already at a station and is not rented")

    query = select(Ride).where(Ride.scooter_id == scooter_id, Ride.status == StatusRide.ACTIVE)
    result = await db.execute(query)
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")

    ride.status = StatusRide.COMPLETED
    ride.end_ride = datetime.now()
    ride.cost = calculate_cost(ride.start_ride, ride.end_ride, scooter.price)

    scooter.is_available = True
    scooter.location = return_data.location

    if return_data.battery_level is not None:
        scooter.battery_level = return_data.battery_level
    
    await db.commit()
    await db.refresh(scooter)
    await db.refresh(ride)
    return scooter
