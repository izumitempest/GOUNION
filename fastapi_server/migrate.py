from sqlalchemy import text
from database import engine

def apply_migration():
    with engine.connect() as conn:
        try:
            print("Checking for 'is_verified' column in 'users' table...")
            # Use raw SQL to add the column if it doesn't exist
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;"))
            conn.commit()
            print("Successfully ensured 'is_verified' column exists.")
        except Exception as e:
            print(f"Migration error: {e}")

if __name__ == "__main__":
    apply_migration()
