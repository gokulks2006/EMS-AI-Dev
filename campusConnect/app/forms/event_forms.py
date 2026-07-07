"""
CampusConnect - Event Forms
=============================
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange

class EventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    venue = StringField("Venue", validators=[DataRequired()])
    
    event_date = DateTimeLocalField(
        "Event Date & Time",
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    
    total_seats = IntegerField(
        "Total Capacity",
        validators=[DataRequired(), NumberRange(min=1)]
    )
