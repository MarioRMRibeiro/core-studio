# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.models import db, User  # Import the database setup
from backend.routes import main  # Import the routes Blueprint
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth  # Import this
from flask_login import LoginManager
import os

app = Flask(__name__)



# Set the secret key to a random string for session management
app.config['SECRET_KEY'] = os.urandom(24)  # Generates a random key


# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:databasepass@localhost/core_studio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

# Define the login view (the route where the user is redirected if not logged in)
login_manager.login_view = 'main.home'

# Define the user_loader callback function
@login_manager.user_loader
def load_user(user_id):
    # Fetch the user from the database based on the user ID
    return User.query.get(int(user_id))
    
# Initialize the database
db.init_app(app)
migrate = Migrate(app, db)

# Register the routes from routes.py
app.register_blueprint(main)

# Main entry point for the app
if __name__ == "__main__":
    app.run(debug=True)

