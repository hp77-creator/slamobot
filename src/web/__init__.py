from flask import Flask

app = Flask(__name__)

from . import routes  # Import routes after app creation to avoid circular imports
