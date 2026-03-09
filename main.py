import os
from app import app

if __name__ == '__main__':
    # Development server - runs with: python main.py
    # In production, gunicorn loads the app from this module directly
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug)
