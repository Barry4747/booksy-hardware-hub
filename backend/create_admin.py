import os
import sys
import getpass
from app.db.base import SessionLocal, engine
from app.models import Base
from app.models.user import User
from app.core.security import get_password_hash

Base.metadata.create_all(bind=engine)

def main():
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    
    if not email:
        email = input("Enter admin email: ").strip()
    if not password:
        password = getpass.getpass("Enter admin password: ").strip()
        
    if not email or not password:
        print("Error: Email and password must be provided.")
        sys.exit(1)
        
    db = SessionLocal()
    
    try:
        existing_admin = db.query(User).filter(User.email == email).first()
        if existing_admin:
            print(f"User with email {email} already exists. Skipping creation.")
            return
            
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print(f"Successfully created admin user: {email}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
