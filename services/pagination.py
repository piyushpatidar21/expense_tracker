from models import Expenses


def pagination_data(page, limit, user_id, db):
    skip = (page - 1) * limit
    get_data = (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return get_data
