import os
import psycopg2
from urllib.parse import urlparse

def migrate():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL não configurada.")
        return

    print(f"Iniciando migração no banco de dados...")
    
    try:
        # Tenta conectar via psycopg2 para garantir compatibilidade com PostgreSQL
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Adiciona a coluna needs_password_reset se ela não existir
        cur.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='user' AND column_name='needs_password_reset') THEN
                    ALTER TABLE "user" ADD COLUMN needs_password_reset BOOLEAN DEFAULT FALSE NOT NULL;
                END IF;
            END $$;
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("Migração concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a migração: {e}")

if __name__ == "__main__":
    migrate()
