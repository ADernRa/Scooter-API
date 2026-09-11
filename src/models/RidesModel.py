from sqlalchemy import String, Boolean, ForeignKey, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime
import enum

from src.models.BaseModel import Base

class StatusRide(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_ride: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_ride: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[StatusRide] = mapped_column(SQLEnum(StatusRide), default=StatusRide.ACTIVE, nullable=False)
    cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    scooter_id: Mapped[int] = mapped_column(ForeignKey("scooters.id"), nullable=False)

    scooter: Mapped["Scooter"] = relationship("Scooter", back_populates="rides")