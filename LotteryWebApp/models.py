import base64
from datetime import datetime

import form as form
import pyotp
from flask_login import UserMixin
import app
import bcrypt
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash


# Encryption
def encrypt(data, draw_key):
    return Fernet(draw_key).encrypt(bytes(data, 'utf-8'))


def decrypt(data, draw_key):
    return Fernet(draw_key).decrypt(data).decode("utf-8")


class User(app.db.Model, UserMixin):
    __tablename__ = 'users'

    id = app.db.Column(app.db.Integer, primary_key=True)

    # User authentication information.
    email = app.db.Column(app.db.String(100), nullable=False, unique=True)
    password = app.db.Column(app.db.String(100), nullable=False)
    pin_key = app.db.Column(app.db.String(100), nullable=False)

    # User information
    firstname = app.db.Column(app.db.String(100), nullable=False)
    lastname = app.db.Column(app.db.String(100), nullable=False)
    phone = app.db.Column(app.db.String(100), nullable=False)
    role = app.db.Column(app.db.String(100), nullable=False, default='user')
    postkey = app.db.Column(app.db.BLOB)

    # Crypto key for user's lottery draws
    draw_key = app.db.Column(app.db.BLOB)

    # Define the relationship to Draw
    draws = app.db.relationship('Draw')

    def __init__(self, email, firstname, lastname, phone, password, role, pin_key=form.pin_key):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = bcrypt.hashpw(User.password.encode('utf-8'), bcrypt.gensalt())
        self.role = role
        self.draw_key = base64.urlsafe_b64encode(bcrypt)
        self.postkey = Fernet.generate_key()
        self.pin_key = pyotp.random_base32()
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


class Draw(app.db.Model):
    __tablename__ = 'draws'

    id = app.db.Column(app.db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = app.db.Column(app.db.Integer, app.db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    # encrypted_data =
    numbers = app.db.Column(app.db.String(100), nullable=False)

    # Draw has already been played (can only play draw once)
    been_played = app.db.Column(app.db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = app.db.Column(app.db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = app.db.Column(app.db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = app.db.Column(app.db.Integer, nullable=False, default=0)

    def __init__(self, user_id, numbers, master_draw, lottery_round, draw_key):
        self.user_id = user_id
        self.numbers = encrypt((numbers, draw_key))
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round

    def update_draw(self, draw, draw_key):
        self.numbers = encrypt(draw, draw_key)
        app.db.session.commit()

    def view_draw(self, draw_key):
        return decrypt(self.numbers, draw_key)


def init_db():
        app.db.drop_all()
        app.db.create_all()

        admin = User(email='admin@email.com', firstname='Alice', lastname='Jones', phone='0191-123-4567',
                     password='Admin1!', role='admin')

        user = User(email='user@email.com', firstname='Bob', lastname='Billy', phone='0191-123-4567', password='User1!',
                    role='user')

        app.db.session.add(admin)
        app.db.session.add(user)
        app.db.session.commit()
