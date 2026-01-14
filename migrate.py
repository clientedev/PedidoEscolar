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

            # Adiciona a coluna file_content na tabela attachment
            inspector_attachment = sa.inspect(db.engine)
            columns_attachment = [c['name'] for c in inspector_attachment.get_columns('attachment')]
            if 'file_content' not in columns_attachment:
                conn.execute(sa.text("ALTER TABLE attachment ADD COLUMN file_content BYTEA"))
                print("Added column 'file_content' to attachment table")
                
        print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
