from app import app

if __name__ == '__main__':
    from app import db
    from apply_migration import run_migration
    with app.app_context():
        # Executa migrações automáticas antes de iniciar
        run_migration()
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
