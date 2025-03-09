import os  # Importing the os module to access environment variables

class Config:
    """Base configuration class that holds common settings."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "sdjg324bsdnfv21490dbfd123214"  # Secret key for session management
    SESSION_TYPE = "filesystem"  # Type of session management

    # Blockchain Node Configuration
    BLOCKCHAIN_HOST = "http://127.0.0.1"  # Host address for the blockchain node
    BLOCKCHAIN_PORT = 8000  # Port number for the blockchain node
    BLOCKCHAIN_URL = f"{BLOCKCHAIN_HOST}:{BLOCKCHAIN_PORT}"  # Complete URL for the blockchain node

class DevelopmentConfig(Config):
    """Development environment settings that extend the base configuration."""
    DEBUG = True  # Enable debug mode for development

class ProductionConfig(Config):
    """Production environment settings that extend the base configuration."""
    DEBUG = False  # Disable debug mode for production

# Set the configuration based on the environment variable
config = DevelopmentConfig if os.environ.get("FLASK_ENV") == "development" else ProductionConfig  # Choose config based on environment
