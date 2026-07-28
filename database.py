import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } if DATABASE_URL.startswith("sqlite") else {}
)

base = declarative_base()

localSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()