# app/schemas.py
from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()

class ProfileSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    zalo_id = fields.Str()
    class Meta:
        fields = ("id","user_id","zalo_id","zalo_name",
                  "zalo_phone","full_name","address","huyen","tinh",
                  "long_pos","lat_pos","created_at","updated_at")
class TimeLogSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    date = fields.Date()
    check_in_time = fields.Time()
    check_out_time = fields.Time()
    overtime = fields.Str()  # Adjust as needed
    late_time = fields.Str()  # Adjust as needed
