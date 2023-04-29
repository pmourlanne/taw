from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, ValidationError

from taw.exceptions import ParsePairingException
from taw.utils import parse_pairings


class PairingsForm(FlaskForm):
    tournament_name = StringField("Tournament Name", validators=[DataRequired()])
    round_number = IntegerField(
        "Round #", validators=[DataRequired(), NumberRange(min=1)]
    )
    aetherhub_dump = TextAreaField(
        "Dump from AetherHub",
        validators=[DataRequired()],
        description="Select your pairings from Aetherhub and copy paste them here",
    )

    def validate_aetherhub_dump(form, field):
        try:
            parse_pairings(field.data)
        except ParsePairingException as e:
            raise ValidationError(str(e)) from e
