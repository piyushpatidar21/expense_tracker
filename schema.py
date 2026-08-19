from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated, Optional
from datetime import date
from enum import Enum


class UserRegister(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=30, description="Choose a unique username"
    )
    email: EmailStr = Field(..., description="Enter a valid email address")
    password: str = Field(
        ..., min_length=6, description="Password must be at least 6 characters"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if not value.isalnum():
            raise ValueError("Username can only contain letters and numbers")
        return value


class UserLogin(BaseModel):
    username: str = Field(..., description="Enter your username or email")
    password: str = Field(..., description="Enter your password")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Enter your registered email address")


class VerifyOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="Enter your registered email address")
    otp: str = Field(
        ..., min_length=4, max_length=10, description="Enter the 6-digit OTP code"
    )


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Enter your registered email address")
    otp: str = Field(
        ..., min_length=4, max_length=10, description="Enter the 6-digit OTP code"
    )
    new_password: str = Field(
        ..., min_length=6, description="Password must be at least 6 characters"
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class CategoryEnum(str, Enum):
    food = "food"
    travel = "travel"
    shopping = "shopping"
    bills = "bills"
    entertainment = "entertainment"


class PaymentEnum(str, Enum):
    cash = "cash"
    upi = "upi"
    credit = "credit"
    debit = "debit"


class UpdateExpense(BaseModel):
    title: str
    amount: float
    category: CategoryEnum
    expense_date: date
    payment_mode: PaymentEnum
    description: str


class UpdateFieldExpense(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[CategoryEnum] = None
    expense_date: Optional[date] = None
    payment_mode: Optional[PaymentEnum] = None
    description: Optional[str] = None


class Expense_Create(BaseModel):
    expense_id: str = Field(
        ...,
        description="Enter Expense ID start with 'e'",
        examples=["e1", "e20"],
        max_length=5,
    )
    title: Annotated[
        Optional[str],
        Field(default=None, description="Enter expense title", example="cloths buy"),
    ]
    amount: float = Field(..., description="Enter expense Amount", gt=0)
    category: CategoryEnum = Field(..., description="Select expense category")
    expense_date: date = Field(
        ..., description="Enter date in format yyyy-mm-dd", example="2026-01-12"
    )
    payment_mode: PaymentEnum = Field(..., description="Select payment mode")
    description: Annotated[
        Optional[str],
        Field(default=None, description="Enter detailed where you spend your money"),
    ]

    @field_validator("expense_id")
    @classmethod
    def validate_expense_id(cls, value: str):
        if not value.startswith("e"):
            raise ValueError("Expense ID must start with 'e'")

        if value.count("e") != 1:
            raise ValueError("Expense ID must contain only one 'e'")

        if not value[1:].isdigit():
            raise ValueError("After 'e', only digits are allowed")

        return value

    @field_validator("expense_date")
    @classmethod
    def validate_expense_date(cls, value: date):
        if value > date.today():
            raise ValueError("Expense date cannot be in the future")
        return value
