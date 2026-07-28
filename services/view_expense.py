from models import Expenses


def view_all_expense(user_id, db):
    return db.query(Expenses).filter(Expenses.user_id == user_id).all()


def view_expense_ID(expense_id, user_id, db):
    db_data = (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id, Expenses.expense_id == expense_id)
        .first()
    )
    return db_data
