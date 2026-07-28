from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    Date,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import base


class User(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    expenses = relationship(
        "Expenses", back_populates="owner", cascade="all, delete-orphan"
    )


class Expenses(base):
    __tablename__ = "expenses"
    __table_args__ = (
        UniqueConstraint("user_id", "expense_id", name="uq_user_expense_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    amount = Column(Float)
    category = Column(String)
    expense_date = Column(Date)
    payment_mode = Column(String)
    description = Column(String)

    owner = relationship("User", back_populates="expenses")
