from marshmallow import Schema, fields, validates, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    name = fields.Str(required=True, validate=fields.validate.Length(min=1, max=100))
    location_name = fields.Str()
    location_lat = fields.Float(dump_only=True)
    location_lng = fields.Float(dump_only=True)
    role = fields.Str(validate=fields.validate.OneOf(['owner', 'renter', 'jammer']), missing='jammer')
    genres_enjoyed = fields.List(fields.Str(validate=fields.validate.OneOf([
        'rock', 'metal', 'jazz', 'blues', 'classical', 'oriental', 'reggae', 'funk', 'pop', 'electronic', 'hiphop'
    ])), missing=[])
    instruments_played = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()), missing=[])
    instruments_owned = fields.List(fields.Str(validate=fields.validate.OneOf([
        'guitar', 'bass', 'drums', 'piano', 'violin', 'oud', 'darbuka', 'zokra', 'doff', 'vocals'
    ])), missing=[])
    is_active_for_jam = fields.Bool(missing=False)
    created_at = fields.DateTime(dump_only=True)

    @validates('instruments_played')
    def validate_instruments_played(self, value):
        valid_instruments = ['guitar', 'bass', 'drums', 'piano', 'violin', 'oud', 'darbuka', 'zokra', 'doff', 'vocals']
        valid_skills = ['beginner', 'intermediate', 'advanced']
        for item in value:
            if not isinstance(item, dict) or 'instrument_type' not in item or 'skill_level' not in item:
                raise ValidationError("Each instrument must have 'instrument_type' and 'skill_level'")
            if item['instrument_type'] not in valid_instruments:
                raise ValidationError(f"Invalid instrument_type: {item['instrument_type']}")
            if item['skill_level'] not in valid_skills:
                raise ValidationError(f"Invalid skill_level: {item['skill_level']}")