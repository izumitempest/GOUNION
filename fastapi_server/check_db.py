import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found")
else:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('users')]
    print(f"Columns in 'users' table: {columns}")
    if 'is_verified' in columns:
        print("is_verified column exists")
    else:
        print("is_verified column MISSING")
