import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "sdjg324bsdnfv21490dbfd123214"
    SESSION_TYPE = "filesystem"

    # Blockchain Node Configuration
    BLOCKCHAIN_HOST = "http://127.0.0.1"
    BLOCKCHAIN_PORT = 8000
    BLOCKCHAIN_URL = f"{BLOCKCHAIN_HOST}:{BLOCKCHAIN_PORT}"

class DevelopmentConfig(Config):
    """Development environment settings."""
    DEBUG = True

class ProductionConfig(Config):
    """Production environment settings."""
    DEBUG = False

# Set the configuration based on the environment variable
config = DevelopmentConfig if os.environ.get("FLASK_ENV") == "development" else ProductionConfig
