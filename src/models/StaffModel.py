from sqlalchemy import String, Boolean, ForeignKey, Float, Date
from sqlalchemy.orm import Mapped,mapped_column, relationship
from datetime import date

from src.models.BaseModel import Base

class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    surname: Mapped[str] = mapped_column(String(30), nullable=False)
    start_work: Mapped[date] = mapped_column(Date, nullable=False)
    job_title: Mapped[str] = mapped_column(String(40), nullable=False)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    users: Mapped["User"] = relationship("User", back_populates="staff")
    station: Mapped["Station"] = relationship("Station", back_populates="staff")