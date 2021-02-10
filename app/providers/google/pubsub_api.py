from app.core.exceptions import *
from typing import Any
from app.core.config import settings
from aiogoogle import Aiogoogle
from .utills import build_service, build_user_creds, build_client_creds
from app.core.schemas.google.gmail_api import *
from google.cloud import pubsub_v1
from google.auth import jwt
import asyncio

class PubSubApiProvider():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_api_provider to create instance")

    @classmethod
    def create_api_provider(cls) -> Any:
        api_provider = cls(direct=False)

        api_provider._setup_credentials()

        api_provider.subscriber = pubsub_v1.SubscriberClient(credentials=api_provider.service_credentials)

        return api_provider

    async def pull(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_pull)

    async def ack(self, ack_ids):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_ack, ack_ids)


    def _sync_ack(self, ack_ids):
        with self.subscriber:
            # Acknowledges the received messages so they will not be sent again.
            self.subscriber.acknowledge(subscription=settings.GOOGLE_PUB_SUB_SUBSCRIPTION_NAME,
                                        ack_ids=ack_ids)


    def _sync_pull(self):
        with self.subscriber:
            # The subscriber pulls a specific number of messages.
            response = self.subscriber.pull(subscription=settings.GOOGLE_PUB_SUB_SUBSCRIPTION_NAME,
                                            max_messages=settings.GOOGLE_PUB_SUB_MAX_MESSAGES)

            message_data = {}
            for received_message in response.received_messages:
                message_data[received_message.ack_id] = received_message.message.data

            return message_data

    def _setup_credentials(self):
        if not settings.PUB_SUB_KEY:
            raise AppErrors(f"PubSubApiProvider.setup_credentials ERROR: there is no PUB_SUB_KEY")

        if not settings.PUB_SUB_CREDENTIALS_AUDIENCE:
            raise AppErrors(f"PubSubApiProvider.setup_credentials ERROR: there is no PUB_SUB_CREDENTIALS_AUDIENCE")

        credentials = jwt.Credentials.from_service_account_info(
            settings.PUB_SUB_KEY,
            audience=settings.PUB_SUB_CREDENTIALS_AUDIENCE
        )

        if not credentials:
            raise AppErrors(f"PubSubApiProvider.setup_credentials ERROR: can't setup credentials")

        self.service_credentials = credentials