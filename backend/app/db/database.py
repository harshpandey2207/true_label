import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# In production, this would be your PostgreSQL URL (e.g., postgresql://user:password@localhost/dbname)
# We use a fallback to SQLite so the cloud demo doesn't crash without a provisioned database.
raw_url = os.getenv("DATABASE_URL", "sqlite:///./metrology.db")

# Automatically fix Render's "postgres://" URL to "postgresql://" which SQLAlchemy requires
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = raw_url

# Postgres requires different connect_args than SQLite
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

