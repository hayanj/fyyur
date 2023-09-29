import os
from flask import Blueprint
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://hayaaljuraysi@localhost:5432/fyyur'

# Blueprints taken from https://flask.palletsprojects.com/en/2.3.x/blueprints/
artists_route = Blueprint('artists', __name__)
shows_route = Blueprint('show', __name__)
venues_route = Blueprint('venues', __name__)