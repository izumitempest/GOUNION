from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import NullPool

SQLALCHEMY_DATABASE_URL = "postgresql://postgres.mswnviziobmmpsrwckjd:Iamlilxeex12354@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"options": "-c search_path=public", "keepalives": 1, "keepalives_idle": 30, "keepalives_interval": 10, "keepalives_count": 5, "prepare_threshold": None},
    poolclass=NullPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()