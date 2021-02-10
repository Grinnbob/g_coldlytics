from app.core.exceptions import *
from typing import Any
from app.services.base_service import CLBaseService
from ..models import *
import json
from pprint import pprint
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from pymongo.errors import BulkWriteError, OperationFailure


class FieldService():
    def __init__(self, service):
        self.service = service

    async def update_custom_fields(self, payload):
        organization = payload['organization']
        belongs_to = payload['belongs_to']
        fields = payload['fields']

        try:
            serialized_fields = {}

            for field in fields:
                serialized_fields[field['id']] = self._serialize_request_field_data(organization=organization,
                                                                                    belongs_to=belongs_to,
                                                                                    data=field)

            total_updated = 0
            operations = []
            collection = CloseComCustomField.collection

            for field_id, data in serialized_fields.items():

                # upsert=True - if you need to create the document if not exist
                operations.append(
                    UpdateOne({"field_id": field_id, "organization": data['organization']},
                              {'$set': data}, upsert=True)
                )

                if len(operations) == 1000:
                    res = await collection.bulk_write(operations, ordered=False)
                    operations = []
                    total_updated += res.modified_count

            if len(operations) > 0:
                res = await collection.bulk_write(operations, ordered=False)
                total_updated += res.modified_count

        except Exception as e:
            pass

        return True

    def _serialize_request_field_data(self,
                                      organization,
                                      belongs_to,
                                      data):
        return dict(name=data['name'],
                    field_id=data['id'],
                    organization=organization,
                    belongs_to=belongs_to,
                    data=data)



