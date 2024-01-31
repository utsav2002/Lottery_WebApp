# IMPORTS
import logging
import os
import socket
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, abort
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from talisman import Talisman

# Importing blueprints
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint
from models import User
from users.views import users_blueprint


# LOGGING
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "Security" in record.getMessage()


fh = logging.FileHandler('lottery.log', 'w')
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

logger = logging.getLogger('')
logger.propagate = False
logger.addHandler(fh)

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise Database
db = SQLAlchemy(app)

# Security Headers
cloudfare_security = {
    'default-src': [
        '\'self\'',
        'link.css'
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\''
    ]
}

talisman = Talisman(app, content_security_policy=cloudfare_security)


# FUNCTIONS
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised access attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return abort(403, 'Forbidden')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('index.html')


# Handling all different types of errors with custom error handlers for each type of error along wth their html template
@app.errorhandler(400)
def error_400(error):
    return render_template('400.html', error=error)


@app.errorhandler(403)
def error_403(error2):
    return render_template('403.html', error=error2)


@app.errorhandler(404)
def error_404(error3):
    return render_template('404.html', error=error3)


@app.errorhandler(500)
def error_500(error4):
    return render_template('500.html', error=error4)


@app.errorhandler(503)
def error_503(error5):
    return render_template('503.html', error=error5)


# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)

# Using the .env file for the SECRET_KEY
load_dotenv()
app = Flask(__name__)
app.config['HelloLotteryApp'] = os.getenv('HelloLotteryApp')

# Using the .env file for the key-pair supplied by Google
app.config['6LfNZFMjAAAAAIO6UDMnvS8N5r8XpnnOjvNtI9-e'] = os.getenv('6LfNZFMjAAAAAIO6UDMnvS8N5r8XpnnOjvNtI9-e')
app.config['6LfNZFMjAAAAAIO6UDMnvS8N5r8XpnnOjvNtI9-e'] = os.getenv('6LfNZFMjAAAAAIO6UDMnvS8N5r8XpnnOjvNtI9-e')

if __name__ == "__main__":
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(lottery_blueprint)

    app.run(host=my_host, port=free_port, debug=True)
