"""The API endpoint definitions.

Functions:
    get_selected_users(
        min_age: int,
        gender: str,
        min_avg_heart_rate: float,
        date_from: str,
        date_to: str): Returns users for given criteria.
    get_user_hourly_heart_rates(user_id: int, date_from: str, date_to: str): Returns hourly heart rates averages for a given user.
"""

import sys
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.storage.models import UserModel
from app.storage.queries import query_users, query_for_user
from .schemas import UserAvgHeartRate, AvgHeartRateByHour


router = APIRouter()

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

date_format = "%d-%m-%Y"
hour_format = "%H:%M"


@router.get("/users", response_model=UserAvgHeartRate, status_code=status.HTTP_200_OK)
async def get_selected_users(
    min_age: int, gender: str, min_avg_heart_rate: float, date_from: str, date_to: str
):
    """
    Get users that are older than `min_age` and have average heart rate
    that is higher than `min_avg_heart_rate` for a given date range.

    Args:

        min_age (int): The minimum user age.
        gender (str): The gender of a user.
        min_avg_heart_rate (float): The minimum average heart rate of a user.
        date_from (str): The start date of the range.
        date_to (str): The end date of the range.

    Returns:

        JSONResponse: A collection of users and their corresponding average heart rate values.
    """

    logger.info(f"Requested users from {date_from} to {date_to}...")
    logger.debug(f"min_age = {min_age}, min_avg_heart_rate = {min_avg_heart_rate}")

    try:
        content = jsonable_encoder(
            tuple(
                UserAvgHeartRate(
                    user=UserModel.model_to_dict(user), avg_heart_rate=avg_heart_rate
                )
                for user, avg_heart_rate in await query_users(
                    min_age=min_age,
                    gender=gender,
                    min_avg_heart_rate=min_avg_heart_rate,
                    date_from=datetime.strptime(date_from, date_format),
                    date_to=datetime.strptime(date_to, date_format),
                )
            )
        )
    except Exception as e:
        logger.error("Could not fetch users: " + str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    return JSONResponse(content=content)


@router.get(
    "/users/{user_id}",
    response_model=AvgHeartRateByHour,
    status_code=status.HTTP_200_OK,
)
async def get_user_hourly_heart_rates(user_id: int, date_from: str, date_to: str):
    """
    Get top `max_results` highest average heart rates for given user ID and dates range.

    Args:

        user_id (int): The related user ID for a heart rate record.
        date_from (str): The start date of the range.
        date_to (str): The end date of the range.

    Returns:

        JSONResponse: A collection of top `max_results` average heart rates grouped by `hour` for a given user.
    """

    logger.info(f"Requested heart rates from {date_from} to {date_to}...")
    logger.debug(f"user_id = {user_id}")
    try:
        content = jsonable_encoder(
            tuple(
                AvgHeartRateByHour(
                    hour=datetime.strftime(hour, hour_format),
                    avg_heart_rate=avg_heart_rate,
                )
                for hour, avg_heart_rate in await query_for_user(
                    user_id=user_id,
                    date_from=datetime.strptime(date_from, date_format),
                    date_to=datetime.strptime(date_to, date_format),
                )
            )
        )
    except Exception as e:
        logger.error("Could not fetch heart rates: " + str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    return JSONResponse(content=content)
