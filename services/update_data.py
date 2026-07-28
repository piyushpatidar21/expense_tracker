from models import Expenses
from fastapi.responses import JSONResponse


def update_data(expense_id, user_id, info, db):
    db_data = (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id, Expenses.expense_id == expense_id)
        .first()
    )
    if not db_data:
        return db_data
    dict_info = info.model_dump()
    for key, value in dict_info.items():
        setattr(db_data, key, value)
    db.commit()
    db.refresh(db_data)
    return JSONResponse(status_code=200, content="Data updated successfully")


def update_expense_field(expense_id, user_id, info, db):
    db_data = (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id, Expenses.expense_id == expense_id)
        .first()
    )
    if not db_data:
        return db_data
    dict_info = info.model_dump(exclude_unset=True)
    for key, value in dict_info.items():
        setattr(db_data, key, value)
    db.commit()
    db.refresh(db_data)
    return JSONResponse(status_code=200, content="Data Updated succefully")
