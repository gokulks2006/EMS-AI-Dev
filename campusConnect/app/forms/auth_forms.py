"""
CampusConnect - Authentication Forms
======================================
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class StudentLoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")



class AdminLoginForm(FlaskForm):
    email = StringField("Admin Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class StudentRegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("College Email", validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    roll_number = StringField("Roll Number", validators=[DataRequired(), Length(max=20)])
    
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo("password", message="Passwords must match.")
    ])


class StudentProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    roll_number = StringField("Roll Number", validators=[DataRequired(), Length(max=20)])
