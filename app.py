from app import app
from config import Config

if __name__ == "__main__":
    app.secret_key = Config.SECRET_KEY
    app.config['SESSION_TYPE'] = Config.SESSION_TYPE
    
    # Run the Flask application
    app.run(debug=True, port=5000)
