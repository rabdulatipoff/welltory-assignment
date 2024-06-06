from typing import Annotated
from pydantic import BaseModel, Field

from app.storage.models import UserModel


class UserAvgHeartRate(BaseModel):
    user: Annotated[dict, UserModel.__dict__]
    avg_heart_rate: Annotated[float, Field(ge=40.0, le=200.0)]


class AvgHeartRateByHour(BaseModel):
    hour: Annotated[str, Field(examples=["%H:%M", "20:00"])]
    avg_heart_rate: Annotated[float, Field(ge=45.0, le=200.0)]
