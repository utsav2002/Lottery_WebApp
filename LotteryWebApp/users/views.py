# IMPORTS
import logging
from datetime import datetime

import pyotp
from flask import Blueprint, render_template, flash, redirect, url_for, request, logging, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from app import db, requires_roles
from models import User
from users import forms
from users.forms import RegisterForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# VIEWS
# view registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # create signup form object
    form = RegisterForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # if this returns a user, then the email already exists in database

        # if email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists!')
            return render_template('register.html', form=form)

        # create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        pin_key=form.pin_key,
                        role='user')

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logging.warning('User Registration [%s, %s]', form.email.data, request.remote_addr)

        # sends user to login page
        return redirect(url_for('users.login'))
    # if request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# view user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    global user
    form = forms.LoginForm()

    # if session attribute logins do not exist, create attribute logins
    if not session.get('logins'):
        session['logins'] = 0

    # if login attempts is 3 or more, generate error message
    elif session.get('logins') >= 3:
        flash("Incorrect Logins exceeded")
        logging.warning("Login Failed (Exceeded login attempts) [%s, %s]", form.email.data, request.remote_addr)

    if form.validate_on_submit():
        # increasing login attempt everytime submit is pressed
        session['logins'] += 1

        user = User.query.filter_by(email=form.email.data).first()

    # Checking credentials

        if not user or not check_password_hash(user.password, form.password.data):
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Login failed, No more attempts left')
            elif session['logins'] == 2:
                flash('Incorrect login details, try again. 1 login attempt left')
            else:
                flash('Incorrect login details, try again. 2 login attempts left')

            logging.warning('Login Failed (Exceeded login attempts) [%s, %s]', form.email.data, request.remote_addr)

            return render_template('login.html', form=form)

        if not pyotp.TOTP(user.pin_key).verify(form.pin):
            flash("Invalid 2FA Token", "Danger!")
            logging.warning('Login failed, 2FA Token Invalid [%s, %s]', form.email.data, request.remote_addr)
            return render_template('login.html', form=form)

        # Resetting login attempts to 0
        session['logins'] = 0

        login_user(user)

        user.last_logged_in = user.current_logged_in
        user.current_logged_in = datetime.now()
        db.session.add(user)
        db.session.commit()

        logging.warning('Log In! [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)

        if current_user.role == 'admin':
            return redirect(url_for('admin.admin'))
        else:
            return redirect(url_for('users.profile'))

    return render_template('login.html', form=form)

# user logout
@users_blueprint.route('/logout')
@login_required
def logout():
    logging.warning('Warning! Log Out! [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))

# view user profile
@users_blueprint.route('/profile')
@login_required
@requires_roles('user')
def profile():
    return render_template('profile.html', name=current_user.firstname)


# view user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)
