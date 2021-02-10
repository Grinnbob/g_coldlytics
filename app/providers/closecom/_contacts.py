from app.core.exceptions import *
import os

class ContactsApi():
    def __init__(self, api_provider):
        self.api_provider = api_provider

    async def run_api(self,
                      api_name,
                      payload,
                      one_page):
        pass

        if not api_name:
            raise AppErrors(f"{os.path.basename(__file__)} ERROR: unknown api_name={api_name}")

