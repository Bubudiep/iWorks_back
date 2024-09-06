# app/schemas.py
from marshmallow import Schema, fields, post_load
from datetime import datetime
from .models import *

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
 
class WorkSalarySchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    class Meta:
        fields = ("id",
            "worksheet_id",
            "SalaryName","isMonthly","checkedDate",
            "Salary","created_at","updated_at")
        
class WorkRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    worksheet_id = fields.Int(required=True)
    workDate = fields.Date(required=True)
    isWorking = fields.Bool(default=True)
    offSpecial = fields.Bool(default=False)
    offRate = fields.Int(default=0, allow_none=True)
    startTime = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    endTime = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    overTime = fields.Float(default=0, allow_none=True)
    lateTime = fields.Float(default=0, allow_none=True)
    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S', dump_only=True)
    updated_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S', dump_only=True)

    @post_load
    def make_workrecord(self, data, **kwargs):
        return WorkRecord(**data)
       
class WorkRecordLTESchema(Schema):
    id = fields.Int(dump_only=True)
    workDate = fields.Date(required=True)
    isWorking = fields.Bool(default=True)
    offSpecial = fields.Bool(default=False)
    offRate = fields.Int(default=0, allow_none=True)
    startTime = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    endTime = fields.DateTime(format='%Y-%m-%d %H:%M:%S', allow_none=True)
    overTime = fields.Int(allow_none=True)
    lateTime = fields.Int(allow_none=True)

    @post_load
    def make_workrecord(self, data, **kwargs):
        return WorkRecord(**data)
      
class WorkSheetSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    class Meta:
        fields = ("id","user_id","Company",
            "isActive","QRCode",
            "created_at","updated_at")
        
class WorkSheetSalarySchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    WorkSalary = fields.List(fields.Nested(WorkSalarySchema), dump_only=True)
    class Meta:
        fields = ("id","WorkSalary",
            "user_id","Company"
            ,"isActive","QRCode",
            "created_at","updated_at")
        
class WorkSheetRecordSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    WorkRecord = fields.List(fields.Nested(WorkRecordSchema), dump_only=True)
    class Meta:
        fields = ("id","WorkRecord",
            "user_id","Company"
            ,"isActive","QRCode",
            "created_at","updated_at")

class WorkSheetDetailsSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    WorkSalary = fields.List(fields.Nested(WorkSalarySchema), dump_only=True)
    WorkRecord = fields.List(fields.Nested(WorkRecordLTESchema), dump_only=True)
    class Meta:
        fields = ("id","WorkRecord","WorkSalary",
            "user_id","Company","NgayNghi","Calamviec","FinishWorkingDay","StartDate"
            ,"isActive","QRCode",
            "created_at","updated_at")

class PhotosSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    class Meta:
        fields = ("id","isActive",
            "filename",
            "filesize",
            "data",
            "user_id","created_at","updated_at")
        