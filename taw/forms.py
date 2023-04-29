from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, ValidationError

from taw.exceptions import ParsePairingException, ParseStandingException
from taw.utils import parse_pairings, parse_standings


class BaseForm(FlaskForm):
    tournament_name = StringField("Tournament Name", validators=[DataRequired()])
    round_number = IntegerField(
        "Round #", validators=[DataRequired(), NumberRange(min=1)]
    )
    aetherhub_dump = TextAreaField(
        "Dump from AetherHub",
        validators=[DataRequired()],
        description="Select your pairings / standings from Aetherhub and copy paste them here",
    )

    class Meta:
        # We don't handle sensitive data, I can't be bothered to set up a secret key properly
        csrf = False


class PairingsForm(BaseForm):
    def validate_aetherhub_dump(form, field):
        try:
            form.parsed_pairings = parse_pairings(field.data)
        except ParsePairingException as e:
            raise ValidationError(str(e)) from e


class StandingsForm(BaseForm):
    def validate_aetherhub_dump(form, field):
        try:
            form.parsed_standings = parse_standings(field.data)
        except ParseStandingException as e:
            raise ValidationError(str(e)) from e
