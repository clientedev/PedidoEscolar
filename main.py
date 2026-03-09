from app import app

if __name__ == '__main__':
    # Development server - runs with: python main.py
    # In production, gunicorn loads the app from this module directly
    app.run(host='0.0.0.0', port=5000, debug=True)
