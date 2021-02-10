from app.core.exceptions import *
from typing import Any
from app.core.config import settings
from aiogoogle import Aiogoogle
from .utills import build_service, build_user_creds, build_client_creds, build_service_creds
from app.core.schemas.google.gmail_api import *
from pprint import pprint

class GDriveServiceApiProvider():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_api_provider to create instance")

        self.user_creds_changed = False

    @classmethod
    async def create_api_provider(cls,
                                  settings: dict=settings.GOOGLE_SERVICE_ACCOUNT_SETTINGS) -> Any:

        api_provider = cls(direct=False)

        api_provider.settings = settings
        api_provider.service = await build_service(name=settings.get('gdrive_api_name'),
                                                   version=settings.get('gdrive_api_version'))

        api_provider.service_creds = build_service_creds(service_creds=settings['credentials'],
                                                         scopes=settings['gdrive_scopes'])


        api_provider.root_folder_id = settings.get('gdrive_root_folder_id')
        if not api_provider.root_folder_id:
            raise AppErrors(f"GOOGLE_GDRIVE_ROOT_FOLDER_ID can't be empty")

        api_provider.leads_template_id = settings.get('gdrive_leads_template_id')
        if not api_provider.leads_template_id:
            raise AppErrors(f"GOOGLE_DRIVE_LEADS_TEMPLATE_ID can't be empty")

        api_provider.stats_template_id = settings.get('gdrive_stats_template_id')
        if not api_provider.stats_template_id:
            raise AppErrors(f"GOOGLE_DRIVE_STATS_TEMPLATE_ID can't be empty")


        return api_provider

    #to view available resources self.service.resources_available
    #to view available methods self.service.methods_available
    #discovery document  self.service.discovery_document

    async def list_folders(self):
        async with Aiogoogle(service_account_creds=self.service_creds) as g:
            request = self.service.files.list()

            folders = []
            full_res = await g.as_service_account(
                request,
                full_res=True)

            async for page in full_res:
                files = page.get('files')
                if files:
                    folders.extend(files)

            return folders

    async def search_file(self, name):
        async with Aiogoogle(service_account_creds=self.service_creds) as g:
            request = self.service.files.list(q=f"name='{name}'")

            res = await g.as_service_account(request)

            if not res:
                return None

            return res.get('files')


    async def copy_file(self,
                        file_id,
                        new_name,
                        parents):

        async with Aiogoogle(service_account_creds=self.service_creds) as g:
            request = self.service.files.copy(fileId=file_id,
                                              json={
                                                "name": new_name,
                                                "parents" : parents
                                                })

            res = await g.as_service_account(request)

            return res


    async def create_folder(self,
                            name,
                            parents):
        exist = await self.search_file(name)
        if exist:
            raise AppErrors(f"drive folder {name} already exists")

        async with Aiogoogle(service_account_creds=self.service_creds) as g:
            request = self.service.files.create(json={
                                                "mimeType" : "application/vnd.google-apps.folder",
                                                "name": name,
                                                "parents" : parents
                                                })

            res = await g.as_service_account(request)

            return res

    async def delete_folder(self, name):
        exist = await self.search_file(name)
        if not exist:
            raise AppErrors(f"drive folder {name} does not exist")

        fileId = exist[0].get('id')
        if not fileId:
            raise AppErrors(f"can't get ID for {name}")

        async with Aiogoogle(service_account_creds=self.service_creds) as g:
            request = self.service.files.delete(fileId=fileId)

            res = await g.as_service_account(request)

            return res

