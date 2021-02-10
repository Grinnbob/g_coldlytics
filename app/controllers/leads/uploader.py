from app.core.exceptions import *
from app.core.schemas.closecom.lead import SpreadSheetLeadCreate
from app.scripts.backend.utils import *
from app.providers.closecom.api_provider import CloseComApiProvider
from app.services.closecom.service import CloseComService
import traceback
from pprint import pprint
from .stats import CrmUploadStats

class LeadsUploader():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_controller to create instance")

        self.gspread_provider = None
        self.stats = CrmUploadStats()

    async def on_shutdown(self):
        if self.closecom_api_session:
            await self.closecom_api_session.close()

    async def create_services(self):
        self.closecom_service = CloseComService()

        self.closecom_api_provider = await CloseComApiProvider.create_api_provider(api_key=self.api_key)
        self.closecom_api_session = await self.closecom_api_provider.get_client_session()


    @classmethod
    async def create_controller(cls,
                                customer_config):

        controller = cls(direct=False)

        controller.customer_config = customer_config.copy()
        controller.customer_name = customer_config.get('name', 'unknown_customer')
        controller.organization = customer_config.get('organization', 'unknown_organization')

        controller.api_key = customer_config.get('api_key')
        if not controller.api_key:
            raise AppErrors(f"ERROR creating: api_key not found for customer={controller.customer_name}")

        await controller.create_services()

        return controller

    async def upload_new(self, system_fields):
        created_leads = await self.closecom_service.find_leads(organization=self.customer_name,
                                                               internal_status='create')

        self.stats.reset_stats()
        inv_lead_custom_fields, inv_concat_custom_fields = await self._inv_custom_fields()
        async for lead in created_leads:
            self.stats.inc_stats_metric('total_leads_to_create')
            try:
                created = await self.create_lead(lead=lead,
                                                 system_fields=system_fields,
                                                 inv_lead_custom_fields=inv_lead_custom_fields,
                                                 inv_concat_custom_fields=inv_concat_custom_fields)
                if created:
                    self.stats.inc_stats_metric('created_success')
                else:
                    self.stats.inc_stats_metric('skipped')
            except Exception as e:
                print(f"UPLOAD_NEW ERROR: for lead={lead.name} error={str(e)}")
                last_error = "upload_new error: " + str(traceback.format_exc())
                await self.closecom_service.update_lead_status(lead=lead,
                                                               internal_status='error',
                                                               last_error=last_error)
                self.stats.inc_stats_metric('errors')

        return self.stats.raw_stats()

    async def upload_updated(self, system_fields):
        updated_leads = await self.closecom_service.find_leads(organization=self.customer_name,
                                                               internal_status='update')

        self.stats.reset_stats()
        inv_lead_custom_fields, inv_concat_custom_fields = await self._inv_custom_fields()
        async for lead in updated_leads:
            self.stats.inc_stats_metric('total_leads_to_update')
            try:
                if lead.lead_id:
                    updated = await self.update_lead(lead,
                                          system_fields=system_fields,
                                          inv_lead_custom_fields=inv_lead_custom_fields,
                                          inv_concat_custom_fields=inv_concat_custom_fields)
                    if updated:
                        self.stats.inc_stats_metric('updated_success')
                    else:
                        self.stats.inc_stats_metric('skipped')

                else:
                    merged = await self.merge_lead(lead,
                                          system_fields=system_fields,
                                          inv_lead_custom_fields=inv_lead_custom_fields,
                                          inv_concat_custom_fields=inv_concat_custom_fields)
                    if merged:
                        self.stats.inc_stats_metric('merged_success')
                    else:
                        self.stats.inc_stats_metric('skipped')

            except Exception as e:
                print(f"UPLOAD_UPDATES ERROR: for lead={lead.name} error={str(e)}")
                last_error = "upload_updated error: " + str(e)
                await self.closecom_service.update_lead_status(lead=lead,
                                                               internal_status='error',
                                                               last_error=last_error)
                self.stats.inc_stats_metric('errors')

        return self.stats.raw_stats()

    async def create_lead(self,
                          lead,
                          system_fields,
                          inv_lead_custom_fields,
                          inv_concat_custom_fields,
                          duplicate_check=True):

        if lead.lead_id:
            await self.closecom_service.update_lead_status(lead=lead,
                                                           internal_status='duplicated_lead_id')
            return None

        if duplicate_check:
            duplicate_id = await self.has_duplicate(lead)
            if duplicate_id:
                await self.closecom_service.update_lead_status(lead=lead,
                                                               internal_status='duplicate')
                return None

        payload = self._post_lead_payload(lead=lead,
                                          system_fields=system_fields,
                                          lead_custom_fields=inv_lead_custom_fields,
                                          contact_custom_fields=inv_concat_custom_fields)


        created = await self.closecom_api_provider.execute(endpoint="leads",
                                                           api_name='post_lead',
                                                           payload=payload)

        if created:
            await self.closecom_service.update_lead(organization=self.customer_name,
                                                    data=created,
                                                    internal_status='uploaded')
        return created

    async def update_lead(self,
                          lead,
                          system_fields,
                          inv_lead_custom_fields,
                          inv_concat_custom_fields):

        if not lead.lead_id:
            raise AppErrors(f"UPDATE ERROR: lead_id can't be empty for lead={lead.id}")

        payload = {
            'lead_id' : lead.lead_id
        }
        current_lead = await self.closecom_api_provider.execute(endpoint="leads",
                                                           api_name='get_lead',
                                                           payload=payload)
        if not current_lead:
            raise AppErrors(f"UPDATE ERROR: lead_id={lead.lead_id} npt found in CRM")

        exclude_emails = self._extract_emails(lead_dict=current_lead)

        payload = self._post_lead_payload(lead=lead,
                                          system_fields=system_fields,
                                          lead_custom_fields=inv_lead_custom_fields,
                                          contact_custom_fields=inv_concat_custom_fields,
                                          exclude_emails=exclude_emails)


        payload['lead_id'] = lead.lead_id
        updated = await self.closecom_api_provider.execute(endpoint="leads",
                                                           api_name='put_lead',
                                                           payload=payload)

        if updated:
            await self.closecom_service.update_lead(organization=self.customer_name,
                                                    data=updated,
                                                    internal_status='uploaded')

        return updated

    #if there is no lead.lead_id in database, then we need to merge
    async def merge_lead(self,
                          lead,
                          system_fields,
                          inv_lead_custom_fields,
                          inv_concat_custom_fields):

        if lead.lead_id:
            raise AppErrors(f"MERGE ERROR: call update_lead for existing lead_id={lead.lead_id}")

        duplicates = await self.get_duplicates(lead)

        #NOTHING to merge, leads doesn't exist
        if not duplicates:
            return await self.create_lead(lead=lead,
                                          system_fields=system_fields,
                                          inv_lead_custom_fields=inv_lead_custom_fields,
                                          inv_concat_custom_fields=inv_concat_custom_fields,
                                          duplicate_check=False)

        exclude_emails = []
        lead_id = None
        for dup in duplicates:
            if dup.get('id'):
                lead_id = dup.get('id')

            excluded = self._extract_emails(dup)
            if excluded:
                exclude_emails.extend(excluded)

        if not lead_id:
            raise AppErrors(f"NEVER HAPPENED MERGE ERROR: can't find lead_id to merge for lead.id={lead.id}")

        payload = self._post_lead_payload(lead=lead,
                                          system_fields=system_fields,
                                          lead_custom_fields=inv_lead_custom_fields,
                                          contact_custom_fields=inv_concat_custom_fields,
                                          exclude_emails=exclude_emails)


        payload['lead_id'] = lead_id
        updated = await self.closecom_api_provider.execute(endpoint="leads",
                                                           api_name='put_lead',
                                                           payload=payload)

        if updated:
            await self.closecom_service.update_lead(organization=self.customer_name,
                                                    data=updated,
                                                    internal_status='uploaded')

        return updated


    async def get_duplicates(self,
                             lead):

        contacts = lead.contacts
        if not contacts:
            return None

        lead_emails = []
        for c in contacts:
            emails = c.get('emails', [])
            for n in emails:
                email = n.get('email', None)
                if email:
                    lead_emails.append(email)

        if not lead_emails:
            return None

        payload = {
            'emails' : lead_emails
        }

        duplicates = await self.closecom_api_provider.execute(endpoint='leads',
                                                              api_name='get_duplicates',
                                                              payload=payload)

        return duplicates

    async def has_duplicate(self,
                              lead):

        duplicates = await self.get_duplicates(lead=lead)
        if not duplicates:
            return None

        if len(duplicates) <= 0:
            return None

        return duplicates[0].get('id', None)

    def _post_lead_payload(self,
                           lead,
                           system_fields,
                           lead_custom_fields,
                           contact_custom_fields,
                           exclude_emails=[]):

        lead_system_fields = system_fields['lead']
        contact_system_fields = system_fields['contact']

        payload = {
            'name' : lead.name
        }

        lead_fields = lead.lead_fields
        for k, v in lead_fields.items():
            custom_name = lead_custom_fields.get(k)

            if k in lead_system_fields:
                payload[k] = v
            elif custom_name:
                payload[custom_name] = v

        contacts = []
        lead_contacts = lead.contacts
        for lc in lead_contacts:
            contact = {}
            for k, v in lc.items():
                custom_name = contact_custom_fields.get(k)
                if k == 'emails':
                    #if any email of the contact in exclude_emails list
                    #we don't add THE WHOLE contact
                    if not exclude_emails:
                        contact['emails'] = v
                    else:
                        accept_contact = True
                        for n in v:
                            if n.get('email', '') in exclude_emails:
                                accept_contact = False
                                break

                        if accept_contact == False:
                            contact = {}
                            break

                        contact['emails'] = v

                elif k in contact_system_fields:
                    contact[k] = v
                elif custom_name:
                    contact[custom_name] = v

            if contact:
                contacts.append(contact.copy())

        if contacts:
            payload['contacts'] = contacts

        if not payload:
            raise AppErrors(f"Can't create payload for lead name={lead.name}")

        return payload

    def _extract_emails(self,
                        lead_dict):
        extracted_emails = []

        contacts = lead_dict.get('contacts', [])
        for contact in contacts:
            item_list = contact.get('emails', [])
            for item in item_list:
                email = item.get('email')
                if email:
                    extracted_emails.append(email)

        return extracted_emails

    async def _inv_custom_fields(self):
        custom_fields = await self.closecom_service.all_custom_fields(organization=self.organization)

        inv_lead_custom_fields = {}
        inv_concat_custom_fields = {}
        async for field in custom_fields:
            if field.belongs_to == 'lead':
                inv_lead_custom_fields[field.name] = "custom." + str(field.field_id)
            elif field.belongs_to == 'contact':
                inv_concat_custom_fields[field.name] = "custom." + str(field.field_id)

        return inv_lead_custom_fields, inv_concat_custom_fields