from app.core.exceptions import *
import os

class CustomFieldsApi():
    def __init__(self, api_provider):
        self.api_provider = api_provider

    async def run_api(self,
                      api_name,
                      payload,
                      one_page):

        if api_name == 'get_custom_field_lead':
            return await self.get_custom_field_lead(payload, one_page)
        elif api_name == 'get_custom_field_contact':
            return await self.get_custom_field_contact(payload, one_page)
        elif api_name == 'post_custom_field_lead':
            return await self.post_custom_field_lead(payload)
        elif api_name == 'post_custom_field_contact':
            return await self.post_custom_field_contact(payload)
        else:
            raise AppErrors(f"{os.path.basename(__file__)} ERROR: unknown api_name={api_name}")

    async def post_custom_field_contact(self,
                                        payload):
        method_name = f"/custom_field/contact/"
        if not payload:
            return None

        return await self.api_provider.post(method_name=method_name,
                                            payload=payload)

    async def post_custom_field_lead(self,
                                        payload):
        method_name = f"/custom_field/lead/"
        if not payload:
            return None

        return await self.api_provider.post(method_name=method_name,
                                            payload=payload)


    async def get_custom_field_lead(self,
                                    payload,
                                    one_page):

        method_name = f"/custom_field/lead/"
        if payload:
            field_id = payload['field_id']
            method_name = method_name + f"/{field_id}/"

        return await self.api_provider.get(method_name=method_name,
                                           one_page=one_page)


    async def get_custom_field_contact(self,
                                    payload,
                                    one_page):

        method_name = f"/custom_field/contact/"
        if payload:
            field_id = payload['field_id']
            method_name = method_name + f"/{field_id}/"

        return await self.api_provider.get(method_name=method_name,
                                           one_page=one_page)