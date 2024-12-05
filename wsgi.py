import sys
import os

# Add your project directory to the sys.path
project_home = u'/home/your_cpanel_username/your_app_directory'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set the environment variable to point to your Flask app
os.environ['FLASK_APP'] = 'app.py'

# Import your Flask app
from app import app as application