from app import app, db
import sqlalchemy as sa
from sqlalchemy import text

def run_migrations():
    """
    Executa migrações automáticas para garantir que o banco de dados
    esteja sempre atualizado com os modelos mais recentes.
    """
    print("Iniciando verificação de estrutura do banco de dados...")
    
    with app.app_context():
        inspector = sa.inspect(db.engine)
        
        # 1. Garantir que as tabelas básicas existam
        db.create_all()
        
        # 2. Verificar e adicionar colunas específicas que podem ter sido adicionadas após a criação inicial
        with db.engine.begin() as conn:
            # Detectar dialeto para tipos específicos
            is_postgres = db.engine.url.drivername.startswith('postgresql')
            blob_type = 'BYTEA' if is_postgres else 'BLOB'
            
            # Tabela: acquisition_request
            columns_req = [c['name'] for c in inspector.get_columns('acquisition_request')]
            
            if 'priority' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN priority VARCHAR(20)"))
                print("Adicionada coluna 'priority' em 'acquisition_request'")
                
            if 'impact' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN impact VARCHAR(50)"))
                print("Adicionada coluna 'impact' em 'acquisition_request'")
                
            if 'estimated_value' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN estimated_value NUMERIC(10, 2)"))
                print("Adicionada coluna 'estimated_value' em 'acquisition_request'")

            if 'final_value' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN final_value NUMERIC(10, 2)"))
                print("Adicionada coluna 'final_value' em 'acquisition_request'")

            if 'classe' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN classe VARCHAR(50) DEFAULT 'ensino' NOT NULL"))
                print("Adicionada coluna 'classe' em 'acquisition_request'")
            
            if 'delivery_deadline' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN delivery_deadline DATE"))
                print("Adicionada coluna 'delivery_deadline' em 'acquisition_request'")
            
            if 'deadline_alert_sent' not in columns_req:
                conn.execute(text("ALTER TABLE acquisition_request ADD COLUMN deadline_alert_sent BOOLEAN DEFAULT FALSE NOT NULL"))
                print("Adicionada coluna 'deadline_alert_sent' em 'acquisition_request'")

            # Tabela: attachment
            columns_att = [c['name'] for c in inspector.get_columns('attachment')]
            if 'file_content' not in columns_att:
                conn.execute(text(f"ALTER TABLE attachment ADD COLUMN file_content {blob_type}"))
                print(f"Adicionada coluna 'file_content' ({blob_type}) em 'attachment'")

            # Tabela: user
            columns_user = [c['name'] for c in inspector.get_columns('user')]
            if 'needs_password_reset' not in columns_user:
                # Usar aspas duplas apenas se necessário para evitar erros em alguns bancos
                user_table = '"user"' if is_postgres else 'user'
                conn.execute(text(f"ALTER TABLE {user_table} ADD COLUMN needs_password_reset BOOLEAN DEFAULT FALSE NOT NULL"))
                print("Adicionada coluna 'needs_password_reset' em 'user'")

        print("Migrações concluídas com sucesso!")

if __name__ == "__main__":
    run_migrations()
