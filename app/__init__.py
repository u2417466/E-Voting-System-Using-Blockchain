# Import the Flask class from the flask module
from flask import Flask

# Import the Config class from the config module
from config import Config

# Create an instance of the Flask class, which will be our WSGI application
app = Flask(__name__, template_folder='../templates')

# Load configuration settings from the Config class
app.config.from_object(Config)

# Import the views module after the app has been initialized
# This ensures that the app context is available for the views
from app import views  
