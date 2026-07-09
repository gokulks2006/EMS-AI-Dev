"""
CampusConnect - Event Forms
=============================
"""

from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, ValidationError


def future_date(form, field):
    """Validator: event date must be in the future."""
    if field.data and field.data <= datetime.now():
        raise ValidationError("Event date must be in the future.")


class EventForm(FlaskForm):
    title = StringField("Event Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    venue = StringField("Venue", validators=[DataRequired()])

    event_date = DateTimeLocalField(
        "Event Date & Time",
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(), future_date]
    )

    total_seats = IntegerField(
        "Total Capacity",
        validators=[DataRequired(), NumberRange(min=1, message="Capacity must be at least 1.")]
    )
