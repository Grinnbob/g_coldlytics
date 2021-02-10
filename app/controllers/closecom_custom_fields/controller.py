from app.core.exceptions import *
from app.providers.closecom.api_provider import CloseComApiProvider
from app.services.closecom.service import CloseComService
from pprint import pprint

class CloseComCustomFieldsController():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_controller to create instance")

        self.gspread_provider = None

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

    async def create_missing_fields(self,
                                    system_fields,
                                    custom_lead_fields,
                                    custom_contact_fields):

        current_lead_fields = await self.get_custom_fields(belongs_to='lead')
        current_contact_fields = await self.get_custom_fields(belongs_to='contact')

        current_lead_fields.extend(system_fields)
        current_contact_fields.extend(system_fields)

        lead_fields_not_exist = [f for f in custom_lead_fields if f not in current_lead_fields]
        contact_fields_not_exist = [f for f in custom_contact_fields if f not in current_contact_fields]

        if lead_fields_not_exist:
            await self.closecom_fields_create(lead_fields_not_exist,
                                             belongs_to='lead')
        else:
            print(f"nothing to create for lead custom fields")

        if contact_fields_not_exist:
            await self.closecom_fields_create(contact_fields_not_exist,
                                             belongs_to='contact')
        else:
            print(f"nothing to create for contact custom fields")



    async def closecom_fields_create(self,
                                     fields,
                                     belongs_to):
        api_name = "post_custom_field_lead"
        if belongs_to == 'contact':
            api_name = "post_custom_field_contact"

        for name in fields:
            try:
                payload = {
                    "name" : name,
                    "type" : "text"
                }

                created = await self.closecom_api_provider.execute(endpoint="custom_fields",
                                                                        api_name=api_name,
                                                                        payload=payload)

                if created:
                    await self.closecom_service.update_custom_fields(organization=self.organization,
                                                                     belongs_to=belongs_to,
                                                                     fields=[created])
                    print(f"FIELD created for {belongs_to}: {name}")
            except Exception as e:
                print(f"PASS: name={name}  response={str(e)}")


    async def get_custom_fields(self,
                            belongs_to):
        cursor =  await self.closecom_service.get_field_names(organization=self.organization,
                                                              belongs_to=belongs_to)
        fields = []

        async for f in cursor:
            fields.append(f.name)

        return fields





    async def update_lead_custom_fields(self):
        lead_fields = await self.closecom_api_provider.execute(endpoint="custom_fields",
                                                                api_name="get_custom_field_lead",
                                                                payload=None,
                                                                one_page=False)

        return await self.closecom_service.update_custom_fields(organization=self.organization,
                                                                belongs_to='lead',
                                                                fields=lead_fields)

    async def update_contact_custom_fields(self):
        contact_fields = await self.closecom_api_provider.execute(endpoint="custom_fields",
                                                               api_name="get_custom_field_contact",
                                                               payload=None,
                                                               one_page=False)

        return await self.closecom_service.update_custom_fields(organization=self.organization,
                                                                belongs_to='contact',
                                                                fields=contact_fields)

