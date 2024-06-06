import random, string, sys
import logging

# NOTE: Use Python 3.12+ for itertools.batched
from itertools import batched  # type: ignore
from datetime import datetime, timedelta
from sqlalchemy import select, insert, delete, text, Result
from sqlalchemy.exc import ResourceClosedError

from .models import UserModel, HeartRateModel, engine, metadata, async_session


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


async def session_transaction(
    query, scalars: bool = False, commit: bool = False
) -> Result | None:
    async with async_session() as session:
        try:
            if scalars:
                result = await session.scalars(query)
            else:
                result = await session.execute(query)
            if commit:
                await session.commit()

            return result
        # Ignore the resource closing automatically on queries that return nothing
        except ResourceClosedError:
            pass
        except Exception as e:
            await session.rollback()
            raise Exception(f"Could not execute query {query}") from e
        finally:
            await session.close()


async def clear_model_table(model):
    await session_transaction(query=delete(model), commit=True)
    # Reset the ID index sequence
    await session_transaction(
        query=text(f"alter sequence {model.__tablename__}_id_seq restart with 1"),
        commit=True,
    )


async def populate_users(
    num_users: int = 1000, batch_size: int = 5000, reset: bool = True
):
    def name(len_from: int = 4, len_to: int = 10):
        return "".join(
            random.choices(string.ascii_lowercase, k=random.randint(len_from, len_to))
        ).capitalize()

    if reset:
        await clear_model_table(UserModel)

    num_added: int = 0
    # Iterate through the chunks range
    for batch in batched(range(num_users), batch_size):
        query = insert(UserModel).values(
            tuple(
                {
                    "name": " ".join((name(), name())),
                    "gender": random.choice(("M", "F")),
                    "age": random.randint(20, 70),
                }
                for _ in batch
            )
        )
        await session_transaction(query=query, commit=True)

        num_added += batch_size
        logger.info(f"Added {min(num_added, num_users)} out of {num_users} records")

    logger.info(f"Created {num_users} user records")


async def populate_heart_rates(
    num_per_user: int = 30, batch_size: int = 10000, reset: bool = True
):
    if reset:
        await clear_model_table(HeartRateModel)

    min_rate = 45.0
    max_rate = 120.0
    start_date = datetime(1980, 1, 1)
    end_date = datetime(2024, 1, 1)

    users = await session_transaction(query=select(UserModel), scalars=True)
    rates = tuple(
        {
            "user_id": user.id,
            "timestamp": start_date
            + timedelta(
                seconds=random.randint(0, int((end_date - start_date).total_seconds()))
            ),
            "heart_rate": round((random.random() * max_rate) + min_rate, 2),
        }
        for user in users  # type: ignore
        for _ in range(num_per_user)
    )

    num_added: int = 0
    # Iterate through the chunks range
    for batch in batched(rates, batch_size):
        query = insert(HeartRateModel).values(batch)
        await session_transaction(query=query, commit=True)

        num_added += batch_size
        logger.info(f"Added {min(num_added, len(rates))} out of {len(rates)} records")

    logger.info(
        f"Created {len(rates)} heart rate records ({num_per_user} records per user)"
    )


async def init_models(reset: bool = True):
    async with engine.begin() as conn:
        if reset:
            await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


async def init_db():
    await init_models()
    await populate_users()
    await populate_heart_rates()
