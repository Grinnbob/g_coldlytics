from app.core.exceptions import *
import os

class LeadsApi():
    def __init__(self, api_provider):
        self.api_provider = api_provider

    async def run_api(self,
                      api_name,
                      payload,
                      one_page):

        if api_name == 'get_lead':
            return await self.get_lead(payload)
        elif api_name == 'post_lead':
            return await self.post_lead(payload)
        elif api_name == 'put_lead':
            return await self.put_lead(payload)
        elif api_name == 'get_duplicates':
            return await self.get_duplicates(payload)
        else:
            raise AppErrors(f"{os.path.basename(__file__)} ERROR: unknown api_name={api_name}")

    async def get_lead(self,
                       payload):
        if not payload or not payload.get('lead_id'):
            return None

        lead_id = payload['lead_id']
        method_name = f"/lead/{lead_id}/"

        return await self.api_provider.get(method_name=method_name)

    async def post_lead(self,
                        payload):
        method_name = f"/lead/"
        if not payload:
            return None

        return await self.api_provider.post(method_name=method_name,
                                            payload=payload)

    async def put_lead(self,
                       payload):
        if not payload:
            return None

        lead_id = payload.get('lead_id')
        if not lead_id:
            return None

        del payload['lead_id']

        method_name = f"/lead/{lead_id}"
        return await self.api_provider.put(method_name=method_name,
                                            payload=payload)


    async def get_duplicates(self,
                             payload):

        method_name = f"/lead/"
        if not payload:
            return None

        emails = payload.get('emails')
        if not emails:
            return None

        emails = list(set(emails))

        search = ''
        i = 0
        for email in emails:
            if i > 0:
                search += ','
            search += f'"{email}"'
            i += 1

        query = f'contact(email(email in ({search})))'

        params = {
            'query' : query,
            '_fields': 'id,contacts'
        }

        ids = await self.api_provider.get(method_name=method_name,
                                           params=params,
                                           one_page=True)

        return ids