import subprocess
import os
import logging
import sys

logger = logging.getLogger(__name__)

def apply_migration():
    """Runs Alembic migrations programmatically to keep the database schema in sync."""
    import os
    # pyrefly: ignore [missing-import]
    from alembic.config import Config
    from alembic import command
    try:
        print("[migration] Running Alembic migrations programmatically...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ini_path = os.path.join(base_dir, "alembic.ini")
        
        # Initialize Alembic config
        alembic_cfg = Config(ini_path)
        # Ensure the script location points to the absolute path of alembic directory
        alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
        
        # Run upgrade head
        command.upgrade(alembic_cfg, "head")
        print("[migration] Database schema is successfully migrated to head.")
    except Exception as e:
        print(f"[migration] Unexpected error during migration: {e}")

if __name__ == "__main__":
    apply_migration()
