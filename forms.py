from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, FileField
from wtforms.validators import InputRequired, Length, ValidationError
from models import User

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username", "class": "form-control", "type": "text", "id": "input-text"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password", "class": "form-control", "type": "password", "id": "input-pass"})

    submit = SubmitField('Login', render_kw={"class": "btn"})

class AccountForm(FlaskForm):
    first_name = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "First Name"})
    
    middle_name = StringField(render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "Middle Name(optional)"})

    last_name = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "Last Name"})

    id_number = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "Enter id number"})

    dob = DateField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "date" ,"placeholder": "Date of birth"})

    email_address = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "email" ,"placeholder": "Email Address"})

    phone_number = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "tel" ,"placeholder": "Enter phone number"})

    alt_phone_number = StringField(render_kw={"class": "account-form-control", "type": "tel" ,"placeholder": "Enter alternate phone number(optional)"})

    home_address = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "Home Address 1"})
    
    alt_home_address = StringField(render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "Home Address 2 (optional)"})

    city = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "City"})

    state = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "State"})

    country = StringField(validators=[
        InputRequired()], render_kw={"class": "account-form-control", "type": "text" ,"placeholder": "Country"})

    zip_code = StringField(validators=[
        InputRequired()], render_kw={"id": "zipCode", "class": "required account-form-control", "type": "number", "placeholder": "Enter zip code"})

    submit = SubmitField('Submit', render_kw={"type": "submit","id": "continue", "class": "btn mx-auto float-md-end py-3 px-5 mt-5 text-7 text-white w-md-25"})