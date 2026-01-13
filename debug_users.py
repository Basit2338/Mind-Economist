from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"User: {u.username}, Password Hash: {u.password_hash}")
