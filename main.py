from pathlib import Path as FilePath

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    BackgroundTasks,
)
from fastapi.middleware.cors import CORSMiddleware
from database import base, engine, get_db
from schema import (
    Expense_Create,
    UpdateExpense,
    UpdateFieldExpense,
    UserRegister,
    UserLogin,
    Token,
    UserOut,
)
from starlette.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from models import User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from services.filter_expense import filter_field, filter_amount
from services.insert_expense import insert_data
from services.update_data import update_data, update_expense_field
from services.delete_expense import delete_expense
from services.view_expense import view_all_expense, view_expense_ID
from services.pagination import pagination_data
from email_utils import send_email

BASE_DIR = FilePath(__file__).resolve().parent
FRONTEND_FILE = BASE_DIR / "frontend.html"

app = FastAPI()

# Allow the frontend (served from a different origin, e.g. a static host or
# the Claude artifact preview) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def middleware_layer(request: Request, call_next):
    print("Request Recieved")
    response = await call_next(request)
    print("Request completed")
    return response


class ExpenseIDNotFoundError(Exception):
    pass


@app.exception_handler(ExpenseIDNotFoundError)
def expense_id_not_found(request: Request, exc: ExpenseIDNotFoundError):
    return JSONResponse(
        status_code=404, content={"message": "Expense ID invalid not found"}
    )


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return FRONTEND_FILE.read_text(encoding="utf-8")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def create_tables():
    base.metadata.create_all(bind=engine)


# Auth route
@app.post(
    "/auth/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
def register(
    info: UserRegister, background_task: BackgroundTasks, db: Session = Depends(get_db)
):
    username = info.username.strip()
    email = info.email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(
            (func.lower(User.username) == username.lower())
            | (func.lower(User.email) == email)
        )
        .first()
    )
    if existing_user:
        if existing_user.username.lower() == username.lower():
            raise HTTPException(status_code=409, detail="Username already taken")
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(info.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    background_task.add_task(
        send_email,
        receiver_email=user.email,
        subject="Welcome to Expense Tracker",
        body=f"""
    Hello {user.username},

    Your account has been created successfully.

    Thank you for registering.

    Regards,
    Expense Tracker Team
    """,
    )
    return JSONResponse(status_code=201, content="Account Registration Succesfully")

    # access_token = create_access_token({"sub": str(user.id)})
    # return {
    #     "access_token": access_token,
    #     "token_type": "bearer",
    #     "username": user.username,
    # }


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
def login(
    info: UserLogin, background_task: BackgroundTasks, db: Session = Depends(get_db)
):
    identifier = info.username.strip().lower()
    user = (
        db.query(User)
        .filter(
            (func.lower(User.username) == identifier)
            | (func.lower(User.email) == identifier)
        )
        .first()
    )
    if not user or not verify_password(info.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    background_task.add_task(
        send_email,
        receiver_email=user.email,
        subject="Expense Tracker Login Successful",
        body=f"""
    Hello {user.username},

    You have successfully logged in to your Expense Tracker account.

    Regards,
    Expense Tracker Team
    """,
    )
    access_token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }


@app.get("/auth/me", response_model=UserOut, tags=["Authentication"])
def me(current_user: User = Depends(get_current_user)):
    return current_user


# Expense routes (all require a logged-in user)
@app.post("/add", tags=["Expenses"])
def add_expenses(
    info: Expense_Create,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return insert_data(info, current_user.id, db)


@app.get("/view", tags=["Expenses"])
def view_all_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return view_all_expense(current_user.id, db)


@app.get("/view/{expense_id}", tags=["Expenses"])
def view_by_expense_ID(
    expense_id: str = Path(
        ..., description="Enter a valid expense ID", examples=["e1", "e2"]
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_data = view_expense_ID(expense_id, current_user.id, db)
    if not db_data:
        raise ExpenseIDNotFoundError
    return db_data


@app.put("/update/{expense_id}", tags=["Expenses"])
def update_expenses(
    expense_id: str,
    info: UpdateExpense,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_data = update_data(expense_id, current_user.id, info, db)
    if not db_data:
        raise ExpenseIDNotFoundError
    return db_data


@app.patch("/update_field/{expense_id}", tags=["Expenses"])
def update_field(
    expense_id: str,
    info: UpdateFieldExpense,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_data = update_expense_field(expense_id, current_user.id, info, db)
    if not db_data:
        raise ExpenseIDNotFoundError
    return db_data


@app.delete("/delete/{expense_id}", tags=["Expenses"])
def delete_expenses(
    expense_id: str = Path(..., description="Enter expense ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_data = delete_expense(expense_id, current_user.id, db)
    if not db_data:
        raise ExpenseIDNotFoundError
    return db_data


@app.get("/filter", tags=["Filtering"])
def filter_by_field(
    category_name: str = Query(
        description="Enter Filter Category like 'bills','entertainment','food','travel','shopping'",
        default=None,
    ),
    payment_mode: str = Query(
        description="Enter payment Mode like 'cash','upi','credit','debit'",
        default=None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return filter_field(category_name, payment_mode, current_user.id, db)


@app.get("/filter_amount", tags=["Filtering"])
def filter_by_amount_range(
    first_amount: float = Query(..., description="Enter first amount range"),
    second_amount: float = Query(..., description="Enter second amount range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return filter_amount(first_amount, second_amount, current_user.id, db)


@app.get("/pagination", tags=["Filtering"])
def pagination_by_limit(
    page: int = Query(1, ge=1, description="page number"),
    limit: int = Query(1, gt=0, lt=100, description="Number of record per page "),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pagination_data(page, limit, current_user.id, db)
