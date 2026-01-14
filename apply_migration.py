from app import app, db
import os

def run_migration():
    with app.app_context():
        # Adiciona a coluna se ela não existir
        try:
            db.session.execute(db.text("ALTER TABLE attachment ADD COLUMN IF NOT EXISTS file_content BYTEA"))
            db.session.commit()
            print("Coluna file_content verificada/adicionada com sucesso.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao executar migração: {e}")

if __name__ == "__main__":
    run_migration()
