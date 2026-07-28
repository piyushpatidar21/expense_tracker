from models import Expenses
from fastapi.responses import JSONResponse


def delete_expense(expense_id, user_id, db):
    db_data = (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id, Expenses.expense_id == expense_id)
        .first()
    )
    if not db_data:
        return db_data
    db.delete(db_data)
    db.commit()
    return JSONResponse(status_code=200, content="Data deleted successfully")
