import os
import sqlalchemy
from sqlalchemy import text
from app import app, db

def migrate():
    print(f"Iniciando migração no banco de dados...")
    
    with app.app_context():
        try:
            # Check if we are using PostgreSQL
            engine_url = str(db.engine.url)
            
            if 'postgresql' in engine_url:
                # PostgreSQL specific migration using DO block
                migration_sql = """
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name='user' AND column_name='needs_password_reset') THEN
                        ALTER TABLE "user" ADD COLUMN needs_password_reset BOOLEAN DEFAULT FALSE NOT NULL;
                    END IF;
                END $$;
                """
            else:
                # SQLite or other (standard SQL with error handling)
                # Note: SQLite doesn't support IF NOT EXISTS in ALTER TABLE easily, 
                # but we can try and catch the error if it already exists
                migration_sql = 'ALTER TABLE "user" ADD COLUMN needs_password_reset BOOLEAN DEFAULT FALSE NOT NULL;'
            
            try:
                db.session.execute(text(migration_sql))
                db.session.commit()
                print("Migração concluída com sucesso!")
            except Exception as e:
                db.session.rollback()
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("Coluna 'needs_password_reset' já existe. Pulando...")
                else:
                    raise e
                    
        except Exception as e:
            print(f"Erro durante a migração: {e}")

if __name__ == "__main__":
    migrate()
