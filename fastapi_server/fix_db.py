import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")


def fix_table(cur, table_name, column_name, references=None):
    print(f"Checking if {column_name} column exists in {table_name} table...")
    cur.execute(
        f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='{table_name}' AND column_name='{column_name}';
    """
    )

    if not cur.fetchone():
        print(f"Adding {column_name} column to {table_name} table...")
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} INTEGER"
        if references:
            sql += f" REFERENCES {references}"
        cur.execute(sql + ";")
        print(f"Column {column_name} added to {table_name} successfully.")
    else:
        print(f"Column {column_name} already exists in {table_name}.")


try:
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    fix_table(cur, "notifications", "group_id", "groups(id)")
    fix_table(cur, "posts", "group_id", "groups(id)")

    conn.commit()
    cur.close()
    conn.close()
    print("Migration finished successfully.")
except Exception as e:
    print(f"Error: {e}")
