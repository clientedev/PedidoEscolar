from app import app, db
import models

def migrate():
    with app.app_context():
        print("Running database migrations...")
        db.create_all()
        print("Database migrations completed successfully.")

if __name__ == "__main__":
    migrate()
