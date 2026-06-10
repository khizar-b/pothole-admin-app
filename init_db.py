import os
import secrets

from app import create_app, bcrypt
from models import db, Admin

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(username='admin').first()
        
        if not existing_admin:
            # Create the initial admin user with a configured or generated password.
            initial_password = os.getenv('ADMIN_PASSWORD') or secrets.token_urlsafe(12)
            password_hash = bcrypt.generate_password_hash(initial_password).decode('utf-8')
            admin = Admin(username='admin', password_hash=password_hash)
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created!")
            print("Username: admin")
            print(f"Password: {initial_password}")
            print("\n⚠️  Save this password now and change it after first login!")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_database()
