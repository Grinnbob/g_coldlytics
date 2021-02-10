from datetime import datetime
from umongo import Document, fields
from app.services import instance, CLBaseModel

@instance.register
class ZBCheck(CLBaseModel, Document):
    key = fields.StringField(required=True, unique=True)
    status = fields.StringField(default="new")

    organization = fields.StringField()
    meta_desc = fields.DictField()

    file_id = fields.StringField()
    file_name = fields.StringField()
    for_check = fields.ListField(fields.StringField())

    email_data = fields.StringField() #json,dumps
    response = fields.ListField(fields.DictField())