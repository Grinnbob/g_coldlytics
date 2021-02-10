from app.core.exceptions import *
from typing import Any
from app.services.base_service import CLBaseService
from ..models import *
import json
from pprint import pprint
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from pymongo.errors import BulkWriteError, OperationFailure

from ._leads import *
from ._fields import *

class CloseComService(CLBaseService):
    def __init__(self):
        super().__init__()

        self.lead_service = LeadService(service=self)
        self.field_service = FieldService(service=self)

    async def update_lead_status(self,
                                 lead,
                                 internal_status,
                                 last_error=""):

        lead.internal_status = internal_status
        lead.last_error = last_error

        await lead.commit()


    async def find_leads(self,
                         organization,
                         internal_status):
        return CloseComLead.find({'organization' : organization, 'internal_status' : internal_status})

    async def all_custom_fields(self,
                                organization):
        return CloseComCustomField.find({'organization' : organization})

    async def get_field_names(self,
                              organization,
                              belongs_to):
        cursor = CloseComCustomField.find({'organization' : organization, 'belongs_to' : belongs_to}, {'name' : 1})
        return cursor


    async def save_from_spreadsheet(self,
                                    leads: dict,
                                    update=False):
        if not leads:
            return False

        if update:
            return await self.lead_service.update_leads(leads)
        else:
            return await self.lead_service.create_leads(leads)


    async def update_lead(self,
                          organization,
                          internal_status,
                          data):

        return await self.lead_service.update_lead(payload=dict(organization=organization,
                                                                data=data,
                                                                internal_status=internal_status))

    async def update_custom_fields(self,
                                    organization,
                                    belongs_to,
                                    fields):

        return await self.field_service.update_custom_fields(payload=dict(
            organization=organization,
            belongs_to=belongs_to,
            fields=fields
        ))
