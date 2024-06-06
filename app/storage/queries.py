from sqlalchemy import select, func
from datetime import datetime

from app.storage.helpers import session_transaction
from app.storage.models import UserModel, HeartRateModel, async_session


# Implement the query_users function
async def query_users(
    min_age: int,
    gender: str,
    min_avg_heart_rate: float,
    date_from: datetime,
    date_to: datetime,
):
    # user_id, avg_heart_rate
    subquery = (
        select(
            HeartRateModel.user_id,
            func.avg(HeartRateModel.heart_rate).label("avg_heart_rate"),
        )
        .filter(HeartRateModel.timestamp.between(date_from, date_to))
        .group_by(HeartRateModel.user_id)
        # Filter by avg heart rate here to save time in parent query
        .having(func.avg(HeartRateModel.heart_rate) >= min_avg_heart_rate)
        .subquery()
    )

    results = await session_transaction(
        select(UserModel, subquery.c.avg_heart_rate)
        .join(subquery, UserModel.id == subquery.c.user_id)
        .filter(UserModel.age >= min_age, UserModel.gender == gender)
    )

    if results:
        return results.all()


# Implement the query_for_user function
async def query_for_user(
    user_id: int, date_from: datetime, date_to: datetime, max_results: int = 10
):
    hourly_avg_subquery = (
        # hour, avg_heart_rate
        select(
            func.date_trunc("hour", HeartRateModel.timestamp).label("hour"),
            func.avg(HeartRateModel.heart_rate).label("avg_heart_rate"),
        )
        .filter(
            HeartRateModel.user_id == user_id,
            HeartRateModel.timestamp.between(date_from, date_to),
        )
        .group_by("hour")
        .subquery()
    )

    results = await session_transaction(
        select(hourly_avg_subquery.c.hour, hourly_avg_subquery.c.avg_heart_rate)
        .order_by(hourly_avg_subquery.c.avg_heart_rate.desc())
        .limit(max_results)
    )

    if results:
        return results.all()
