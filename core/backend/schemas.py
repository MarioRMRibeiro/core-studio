from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)


class AppointmentSchema(Schema):
    name = fields.Str(required=True)
    date = fields.Str(required=True)
    time = fields.Str(required=True)
    tipo = fields.Str(required=True)

appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)
