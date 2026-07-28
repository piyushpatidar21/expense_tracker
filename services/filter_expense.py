from models import Expenses
from fastapi import HTTPException


def filter_field(category_name, payment_mode, user_id, db):
    query = db.query(Expenses).filter(Expenses.user_id == user_id)

    if category_name is not None:
        query = query.filter(Expenses.category == category_name)

    if payment_mode is not None:
        query = query.filter(Expenses.payment_mode == payment_mode)

    db_data = query.all()

    if not db_data:
        return {"message": "No expenses found."}

    return db_data


def filter_amount(first_amount, second_amount, user_id, db):
    base_query = db.query(Expenses).filter(Expenses.user_id == user_id)

    min_data = base_query.order_by(Expenses.amount.asc()).first()
    max_data = base_query.order_by(Expenses.amount.desc()).first()

    if not min_data or not max_data:
        return {"message": "No expenses found."}

    min_num = min_data.amount
    max_num = max_data.amount

    if first_amount >= min_num and max_num <= second_amount:
        raise HTTPException(status_code=422, detail="Error: Invalid amount range")

    db_data = base_query.filter(
        Expenses.amount >= first_amount, Expenses.amount <= second_amount
    ).all()
    return db_data
