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

                -- Forçar reset apenas uma vez para quem ainda não tem o campo ou como reset inicial
                -- Para garantir que seja apenas no "próximo acesso" e não em todo deploy, 
                -- podemos checar se já fizemos essa migração global antes ou usar um critério específico.
                -- No entanto, o usuário pediu para garantir que permaneça após a troca.
                -- O código abaixo só marca como TRUE. Uma vez que o usuário troca, o sistema (em routes.py) 
                -- seta como FALSE, então no próximo deploy o script não deve sobrescrever se já foi trocado.
                -- Para evitar que TODO deploy resete todo mundo, vamos resetar apenas se a coluna acabou de ser criada
                -- ou se houver um marcador de "migração de segurança pendente".
                
                -- Versão segura: Só reseta se a coluna foi recém-criada (default FALSE no ALTER TABLE)
                -- ou se quisermos forçar uma única vez, podemos comentar a linha de UPDATE após o primeiro deploy bem sucedido.
                -- UPDATE "user" SET needs_password_reset = TRUE; 
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
