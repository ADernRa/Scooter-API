from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from models.RidesModel import StatusRide
from datetime import datetime
from typing import Optional


class RideBase(BaseModel):
    start_ride: datetime = Field(...)
    end_ride: Optional[datetime] = None
    status: StatusRide = Field(...)
    cost: float = Field(...)

class RideResponde(RideBase):
    id: int
    scooter_id: int


    model_config = ConfigDict(from_attributes=True)