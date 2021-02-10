from datetime import datetime
from umongo import Document, fields
from app.services import instance, CLBaseModel

@instance.register
class ZBEmail(CLBaseModel, Document):
    email = fields.StringField(required=True, unique=True)
    status = fields.StringField(default="new")

    zb_response = fields.DictField()