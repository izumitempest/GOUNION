# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "").strip()

# Supabase (and some Heroku-style providers) give postgres:// but SQLAlchemy
# requires postgresql://
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

# If the URL is empty or still a placeholder, fall back to local SQLite
_is_postgres = _raw_url.startswith("postgresql://")

if _is_postgres:
    SQLALCHEMY_DATABASE_URL = _raw_url
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "options": "-c search_path=public",
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
        pool_size=20,
        max_overflow=10,
        pool_timeout=60,
        pool_recycle=300,
        pool_pre_ping=True,
    )
    print("[db] Connected to PostgreSQL database.")
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    print("[db] WARNING: DATABASE_URL not set or invalid — using local SQLite fallback.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
