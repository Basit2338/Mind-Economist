from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if admin exists
    if not User.query.filter_by(username='admin').first():
        print("Creating admin user...")
        hashed_pw = generate_password_hash('admin123')
        admin = User(username='admin', password_hash=hashed_pw)
        db.session.add(admin)
        db.session.commit()
        print("Admin created. Username: admin, Password: admin123")
    else:
        print("Admin user already exists.")
