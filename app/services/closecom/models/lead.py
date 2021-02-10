from datetime import datetime
from umongo import Document, fields
from app.services import instance, CLBaseModel

@instance.register
class CloseComLead(CLBaseModel, Document):
    name = fields.StringField()
    lead_id = fields.StringField(unique=True, sparse=True)

    organization = fields.StringField(required=True)
    internal_status = fields.StringField(required=True)
    contacts = fields.ListField(fields.DictField())
    lead_fields = fields.DictField()

    status_id = fields.StringField()
    organization_id = fields.StringField()

    data = fields.DictField()
    last_error = fields.StringField()

    class Meta:
        indexes = ({'key': ['organization', 'name'], 'unique': True},)
