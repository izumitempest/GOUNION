import os
import sys
import argparse
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import the fastapi_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_server.database import SessionLocal
from fastapi_server.models import User

def make_admin(email: str = None, user_id: str = None):
    db: Session = SessionLocal()
    try:
        user = None
        if email:
            print(f"Looking for user with email: {email}")
            user = db.query(User).filter(User.email == email).first()
        elif user_id:
            print(f"Looking for user with ID: {user_id}")
            user = db.query(User).filter(User.id == user_id).first()
        else:
            print("Error: You must provide either an email or a user_id.")
            return

        if not user:
            print("Error: User not found in the database. Are you sure they are registered?")
            return

        print(f"Found user: {user.username} ({user.email})")
        print(f"Current role: {user.role}")

        if user.role == "admin":
            print("User is already an admin. No changes made.")
            return

        user.role = "admin"
        db.commit()
        print("Success! User has been elevated to 'admin'. They can now access the admin panel.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Elevate a user to admin status in GoUnion.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--email", "-e", help="The email address of the user to make admin.")
    group.add_argument("--id", "-i", help="The UUID of the user to make admin.")
    
    args = parser.parse_args()
    
    make_admin(email=args.email, user_id=args.id)
