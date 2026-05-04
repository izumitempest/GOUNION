import subprocess
import os
import logging

logger = logging.getLogger(__name__)

def apply_migration():
    """Runs Alembic migrations to keep the database schema in sync."""
    try:
        # Determine the directory where alembic.ini is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try to run alembic upgrade head
        # We use 'python -m alembic' to ensure we use the same environment
        print("[migration] Running Alembic migrations...")
        result = subprocess.run(
            ["python3", "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=base_dir
        )
        
        if result.returncode == 0:
            print("[migration] Database schema is up to date.")
            if result.stdout.strip():
                print(result.stdout)
        else:
            # If python3 -m alembic fails, try just 'alembic'
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=base_dir
            )
            if result.returncode == 0:
                print("[migration] Database schema is up to date (via standalone alembic).")
            else:
                print(f"[migration] Alembic migration failed: {result.stderr}")
                
    except Exception as e:
        print(f"[migration] Unexpected error during migration: {e}")

if __name__ == "__main__":
    apply_migration()
