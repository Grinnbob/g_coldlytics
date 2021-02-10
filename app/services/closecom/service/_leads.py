from app.core.exceptions import *
from typing import Any
from app.services.base_service import CLBaseService
from ..models import *
import json
from pprint import pprint
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne
from pymongo.errors import BulkWriteError, OperationFailure


class LeadService():
    def __init__(self, service):
        self.service = service

    #change to Schema
    async def update_lead(self, payload):
        organization = payload['organization']
        data = payload['data']
        internal_status = payload['internal_status']

        collection = CloseComLead.collection
        await collection.update_one({'name': data['name'], 'organization' : organization}, {
            '$set': {
                'lead_id': data.get('id', ''),
                'status_id': data.get('status_id', ''),
                'internal_status' : internal_status,
                'organization_id' : data.get('organization_id', ''),
                'data' : data
            }
        }, upsert=True)


    async def update_leads(self, leads):
        total_updated = 0
        try:
            operations = []
            collection = CloseComLead.collection

            for lead_name, data in leads.items():

                #upsert=True - if you need to create the document if not exist
                operations.append(
                    UpdateOne({"name" : lead_name, "organization" : data['organization']},
                              {'$set' : data}, upsert=True)
                )

                if len(operations) == 1000:
                    res = await collection.bulk_write(operations, ordered=False)
                    operations = []
                    total_updated += res.modified_count
                    total_updated += res.inserted_count
                    total_updated += res.upserted_count

            if len(operations) > 0:
                res = await collection.bulk_write(operations, ordered=False)
                total_updated += res.modified_count
                total_updated += res.inserted_count
                total_updated += res.upserted_count

        except Exception as e:
            pass

        return total_updated

    async def create_leads(self, leads):
        created = 0
        res = None
        try:
            leads_list = []

            for lead_name, data in leads.items():
                leads_list.append(data)

            collection = CloseComLead.collection
            res = await collection.insert_many(leads_list, ordered=False)

            if res:
                created = len(res.inserted_ids)

        except OperationFailure as dup:
            if dup.details.get('writeErrors'):
                created = dup.details.get('nInserted', 0)

        except Exception as e:
            print(f"ERROR: _spreadsheet_create_leads: {str(e)}")


        return created


