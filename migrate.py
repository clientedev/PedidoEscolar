from app import app, db
import sqlalchemy as sa

def migrate():
    with app.app_context():
        inspector = sa.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('acquisition_request')]
        
        with db.engine.begin() as conn:
            if 'priority' not in columns:
                conn.execute(sa.text("ALTER TABLE acquisition_request ADD COLUMN priority VARCHAR(20)"))
                print("Added column 'priority'")
            
            if 'impact' not in columns:
                conn.execute(sa.text("ALTER TABLE acquisition_request ADD COLUMN impact VARCHAR(50)"))
                print("Added column 'impact'")
                
        print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
