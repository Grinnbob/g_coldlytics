from app.core.exceptions import *
from typing import Any
from app.core.config import settings
from aiogoogle import Aiogoogle
from .utills import build_service, build_user_creds, build_client_creds
from app.core.schemas.google.gmail_api import *
from app.core.schemas.topics.watch import WatchModel

class GmailApiProvider():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_api_provider to create instance")

        self.user_creds_changed = False

    @classmethod
    async def create_api_provider(cls,
                                  user_creds: dict,
                                  settings: dict=settings.GOOGLE_CLIENT_SETTINGS) -> Any:

        api_provider = cls(direct=False)

        api_provider.settings = settings
        api_provider.service = await build_service(name=settings.get('gmail_api_name'),
                                                   version=settings.get('gmail_api_version'))

        api_provider.user_creds = build_user_creds(user_creds)
        api_provider.client_creds = build_client_creds(client_creds=settings['credentials'],
                                                       scopes=settings['gmail_scopes'])

        return api_provider

    #RESPONSE example
    # {'emailAddress': 'ks.shilov@gmail.com', 'messagesTotal': 482326, 'threadsTotal': 338293, 'historyId': '38695195'}
    async def get_profile(self, user_id='me'):
        async with Aiogoogle(user_creds=self.user_creds,
                            client_creds=self.client_creds) as g:

            request = self.service.users.getProfile(userId=user_id)

            res = await g.as_user(request)

            self.update_user_creds(g.user_creds)

            return GetPrfole(**res)

    async def messages_list(self,
                            user_id:str,
                            labels_ids: list = [],
                            next_page_token: str = None,
                            pages_count: int = settings.NEXT_PAGE_ITER_COUNT):

        async with Aiogoogle(user_creds=self.user_creds,
                            client_creds=self.client_creds) as g:
            req = {
                'userId' : user_id
            }
            if labels_ids:
                req['labelIds'] = labels_ids
            if next_page_token:
                req['pageToken'] = next_page_token

            request = self.service.users.messages.list(**req)

            response = await g.as_user(request,
                                        full_res=True)
            messages = []
            page_token = None
            count = 0
            raw_response = {}
            async for next_page in response:
                if 'messages' in next_page:
                    messages.extend(next_page['messages'])

                raw_response = next_page
                page_token = next_page.get('nextPageToken', None)
                count += 1
                if count >= pages_count:
                    break

            res = MessagesList(
                messages=messages,
                next_page_token=page_token
            )

            if not messages:
                res.error = True
                res.response = raw_response

            self.update_user_creds(g.user_creds)

            return res

    async def list_labels(self, user_id='me'):
        async with Aiogoogle(user_creds=self.user_creds,
                            client_creds=self.client_creds) as g:

            request = self.service.users.labels.list(userId=user_id)

            res = await g.as_user(request)

            self.update_user_creds(g.user_creds)

            if not res.get('labels'):
                return []

            return res['labels']

    async def watch(self, user_id, labels):
        async with Aiogoogle(user_creds=self.user_creds,
                            client_creds=self.client_creds) as g:

            body = {
                'labelIds' : labels,
                'labelFilterAction' : 'INCLUDE',
                'topicName': settings.GOOGLE_GMAIL_API_PUSH_TOPIC
            }
            request = self.service.users.watch(userId=user_id,
                                               body=body)

            res = await g.as_user(request)

            self.update_user_creds(g.user_creds)

            if not res.get('historyId'):
                raise AppErrors(f"watch error for user_id={user_id} res={res}")

            return WatchModel(
                action='watch',
                account=user_id,
                history_id=res['historyId'],
                expiration=res['expiration']
            )


    async def stop(self, user_id):
        async with Aiogoogle(user_creds=self.user_creds,
                            client_creds=self.client_creds) as g:

            request = self.service.users.stop(userId=user_id)

            res = await g.as_user(request)

            self.update_user_creds(g.user_creds)

            if res:
                raise AppErrors(f"stop error for user_id={user_id} res={res}")

            return WatchModel(
                action='stop',
                account=user_id
            )


    def update_user_creds(self, new_creds):
        if self.user_creds != new_creds:
            self.user_creds = new_creds
            self.user_creds_changed = True

    def user_creds_accepted(self):
        self.user_creds_changed = False
