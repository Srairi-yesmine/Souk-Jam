from marshmallow import Schema, fields

class RentalSchema(Schema):
    id = fields.Int(dump_only=True)
    instrument_id = fields.Int(required=True)
    renter_id = fields.Int(dump_only=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    total_price = fields.Float(dump_only=True)
    status = fields.Str(validate=fields.validate.OneOf(['pending', 'confirmed', 'completed', 'cancelled']))
    created_at = fields.DateTime(dump_only=True)