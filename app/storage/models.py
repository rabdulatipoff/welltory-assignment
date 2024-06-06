from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    backref,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import DB_CONFIG


class Base(DeclarativeBase):
    @staticmethod
    def model_to_dict(model: object):
        """Return the object's dict excluding private attributes,
        sqlalchemy state and relationship attributes."""

        exclude = ("_sa_adapter", "_sa_instance_state")
        return {
            k: v
            for k, v in vars(model).items()
            if not k.startswith("_") and not any(hasattr(v, a) for a in exclude)
        }

    def __repr__(self):
        params = ", ".join(f"{k}={v}" for k, v in self.model_to_dict(self).items())
        return f"{self.__class__.__name__}({params})"


# Define tables
# Singular form naming for better readability
class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    # integer type for indexing & query performance
    age: Mapped[int] = mapped_column(Integer, index=True)
    heart_rates: Mapped[list["HeartRateModel"]] = relationship(
        "HeartRateModel", backref="user", cascade="all, delete-orphan"
    )


class HeartRateModel(Base):
    __tablename__ = "heart_rate"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # indexed for quicker user lookups
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(UserModel.id, onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
    )
    # indexed for faster hourly aggregation
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    heart_rate: Mapped[float] = mapped_column(Float)


# Set up database-related objects
# Using NullPool for easy horizontal scaling of connections
engine = create_async_engine(
    f"postgresql+asyncpg://{DB_CONFIG['user']}:{DB_CONFIG['pass']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}",
    poolclass=NullPool,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore
metadata = Base.metadata
