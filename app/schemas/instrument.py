from marshmallow import Schema, fields

class InstrumentSchema(Schema):
    id = fields.Int(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=fields.validate.Length(min=1, max=100))
    brand = fields.Str(validate=fields.validate.Length(max=50))
    type = fields.Str(required=True, validate=fields.validate.Length(min=1, max=50))
    description = fields.Str()
    status = fields.Str(validate=fields.validate.OneOf(['available', 'rented', 'unavailable']))
    price_per_day = fields.Float(required=True, validate=fields.validate.Range(min=0))
    photo_url = fields.Str(dump_only=True)
    location_name = fields.Str()
    location_lat = fields.Float(dump_only=True)
    location_lng = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)