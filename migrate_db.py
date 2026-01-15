import os
import sqlalchemy
from sqlalchemy import text
from app import app, db

def migrate():
    print(f"Iniciando migração no banco de dados PostgreSQL...")
    
    with app.app_context():
        try:
            # Drop constraint if exists to avoid issues, then add column
            # Using raw SQL for precision in PostgreSQL
            migration_sql = """
            DO $$ 
            BEGIN 
                -- Adiciona a coluna se não existir
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='user' AND column_name='needs_password_reset') THEN
                    ALTER TABLE "user" ADD COLUMN needs_password_reset BOOLEAN DEFAULT FALSE NOT NULL;
                    RAISE NOTICE 'Coluna needs_password_reset adicionada.';
                ELSE
                    RAISE NOTICE 'Coluna needs_password_reset já existe.';
                END IF;

                -- Forçar reset para todos os usuários por segurança no próximo acesso
                UPDATE "user" SET needs_password_reset = TRUE;
                RAISE NOTICE 'Reset de senha forçado para todos os usuários.';
            END $$;
            """
            
            db.session.execute(text(migration_sql))
            db.session.commit()
            print("Migração PostgreSQL concluída com sucesso!")
                    
        except Exception as e:
            db.session.rollback()
            print(f"Erro durante a migração: {e}")

if __name__ == "__main__":
    migrate()
