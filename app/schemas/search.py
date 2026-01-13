from marshmallow import Schema, fields

class SearchInstrumentSchema(Schema):
    location_lat = fields.Float()
    location_lng = fields.Float()
    radius_km = fields.Float(validate=fields.validate.Range(min=0))
    type = fields.Str()
    price_min = fields.Float(validate=fields.validate.Range(min=0))
    price_max = fields.Float(validate=fields.validate.Range(min=0))
    status = fields.Str(validate=fields.validate.OneOf(['available', 'rented', 'unavailable']))
    limit = fields.Int(validate=fields.validate.Range(min=1, max=100), default=20)