# Import the Flask application instance from the app module
from app import app
# Import configuration settings from the config module
from config import Config

# Check if the script is being run directly (not imported as a module)
if __name__ == "__main__":
    # Set the secret key for the application from the configuration
    app.secret_key = Config.SECRET_KEY
    # Set the session type for the application from the configuration
    app.config['SESSION_TYPE'] = Config.SESSION_TYPE
    
    # Run the Flask application with debug mode enabled and on port 5000
    app.run(debug=True, port=5000)
