from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('log in')


class RegisterForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    repassword = PasswordField('repassword', validators=[DataRequired()])
    submit = SubmitField('regist')


class TextForm(FlaskForm):
    text = TextAreaField("text", validators=[DataRequired()])
    submit = SubmitField('send')


class ChatInviteForm(FlaskForm):
    user_id = StringField("user_id", validators=[DataRequired()])
    submit = SubmitField('invite')


class ChatCreateForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    submit = SubmitField('send')