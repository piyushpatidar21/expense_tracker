from fastapi import HTTPException
from models import Expenses


def insert_data(info, user_id, db):
    existing_expense = (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id, Expenses.expense_id == info.expense_id)
        .first()
    )

    if existing_expense:
        raise HTTPException(status_code=409, detail="Expense ID already exists")

    db_info = Expenses(**info.model_dump(), user_id=user_id)

    db.add(db_info)
    db.commit()
    db.refresh(db_info)

    return {"message": "Data inserted successfully"}
