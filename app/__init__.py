from flask import Flask
from config import Config

app = Flask(__name__, template_folder='../templates')

# Load configuration settings
app.config.from_object(Config)

from app import views  # Import views after app initialization
