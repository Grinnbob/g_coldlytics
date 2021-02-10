from datetime import datetime
from umongo import Document, fields
from app.services import instance, CLBaseModel

@instance.register
class CloseComCustomField(CLBaseModel, Document):
    name = fields.StringField(required=True)
    belongs_to = fields.StringField(required=True) # lead, contact, activity

    field_id = fields.StringField(required=True)

    organization = fields.StringField(required=True)
    data = fields.DictField()

    class Meta:
        indexes = ({'key': ['name', 'belongs_to', 'organization'], 'unique': True},)
