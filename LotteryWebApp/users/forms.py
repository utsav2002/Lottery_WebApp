from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField, validators, EmailField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, NoneOf, Regexp, Length


class RegisterForm(FlaskForm):
    email = EmailField(validators=[Email(message='Must be a valid email address'), validators.DataRequired()])
    firstname = StringField(validators=[NoneOf(
        ['*', '?', '!', '+', '^', '+', '%', '&', '/', '(', ')', '=', '}', ']', '[', '{', '$', '#', '@', '<', '>', ],
        message="First name must not contain any of these: * ? ! ^ + % & / ( ) = } ] [ { $ # @ < > ' "),
        validators.DataRequired()])
    lastname = StringField(validators=[NoneOf(
        ['*', '?', '!', '+', '^', '+', '%', '&', '/', '(', ')', '=', '}', ']', '[', '{', '$', '#', '@', '<', '>', ],
        message="Last name must not contain any of these: * ? ! ^ + % & / ( ) = } ] [ { $ # @ < > ' "),
        validators.DataRequired()])
    phone = StringField(validators=[Regexp(regex=r"^\d{3}[-]{1}\d{3}[-]{1}\d{4}$",
                                           message="Enter phone number in this format: xxx-xxx-xxxx"),
                                    validators.DataRequired()])
    password = PasswordField(validators=[Regexp(regex=r"[A-Za-z0-9@#$%^&+=]{6,12}",
                                                message='Your password must be between 6 to 12 digits, contain at one '
                                                        'upper and lower case character, and at least one digit and '
                                                        'a special character'), validators.DataRequired()])
    confirm_password = PasswordField(
        validators=[EqualTo('password', message="The password doesn't match"), validators.DataRequired()])
    pin_key = StringField(validators=[Length(min=32, max=32, message="Pin-Key must be exactly 32 characters long!"),
                                      validators.DataRequired()])
    submit = SubmitField()


# Hashing the password entered by the user while registering so that it is not readable in the database
# password_hash = bcrypt.hashpw(RegisterForm.password.encode('utf-8'), bcrypt.gensalt())

class LoginForm(FlaskForm):

    def __init__(self, formdata=_Auto, **kwargs):
        super().__init__(formdata, kwargs)
        self.email = None

    username = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    pin = IntegerField(validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
