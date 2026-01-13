from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    target_username = "Basit"
    target_password = "Basit@2338"
    hashed_pw = generate_password_hash(target_password)
    
    # Check if 'Basit' already exists
    user_basit = User.query.filter_by(username=target_username).first()
    
    if user_basit:
        print(f"User '{target_username}' found. Updating password...")
        user_basit.password_hash = hashed_pw
        db.session.commit()
        print("Password updated successfully.")
    else:
        # Check if 'admin' exists to rename
        user_admin = User.query.filter_by(username="admin").first()
        if user_admin:
            print(f"User 'admin' found. Renaming to '{target_username}' and updating password...")
            user_admin.username = target_username
            user_admin.password_hash = hashed_pw
            db.session.commit()
            print("Admin renamed and password updated successfully.")
        else:
            print(f"No existing admin found. Creating user '{target_username}'...")
            new_admin = User(username=target_username, password_hash=hashed_pw)
            db.session.add(new_admin)
            db.session.commit()
            print(f"User '{target_username}' created successfully.")
