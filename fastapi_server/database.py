# database.py

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

_raw_url = os.getenv("DATABASE_URL", "").strip()

# Supabase (and some Heroku-style providers) give postgres:// but SQLAlchemy
# requires postgresql://
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

# If the URL is empty or still a placeholder, fall back to local SQLite
_is_postgres = _raw_url.startswith("postgresql://")

if _is_postgres:
    _db_url = make_url(_raw_url)
    _is_supabase = "supabase.com" in (_db_url.host or "")
    if _is_supabase and _db_url.port != 6543:
        _db_url = _db_url.set(port=6543)

    SQLALCHEMY_DATABASE_URL = _db_url.render_as_string(hide_password=False)
    _connect_args = {
        "options": "-c search_path=public",
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
    if _is_supabase and "sslmode" not in _db_url.query:
        _connect_args["sslmode"] = "require"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=_connect_args,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "2")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
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
