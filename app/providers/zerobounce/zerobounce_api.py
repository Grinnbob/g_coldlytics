from app.core.exceptions import *
from app.core.config import settings
from typing import Any
from app.core.config import settings
import aiohttp
from aiohttp import BasicAuth
import traceback
import os
import io
from requests_toolbelt.multipart.encoder import MultipartEncoder
from io import BytesIO
import json
import sys
from pathlib import Path
from app.files.zerobounce import zb_files_directory
from .zerobounce_bulk_api import *

class ZerobounceApiProvider():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_api_provider to create instance")

        self.session = None

    @classmethod
    async def create_api_provider(cls,
                                  settings: dict=settings.ZEROBOUNCE_API_SETTINGS) -> Any:

        api_provider = cls(direct=False)

        api_provider.api_settings = settings
        api_provider.api_key = settings['api_key']

        zb_init(api_provider.api_key)

        return api_provider

    async def get_client_session(self):
        if self.session:
            raise AppErrors("Session already created - use ONE session per app")

        self.session = aiohttp.ClientSession()

        return self.session


    async def get_credits(self):
        if not self.session:
            raise AppErrors("Call get_client_session first")

        prepared_request = self._prepare_request(method_name=f"/getcredits")

        return await self._dispatch(prepared_request=prepared_request,
                                    command='get_credits')

    async def validate_email(self, email):
        if not self.session:
            raise AppErrors("Call get_client_session first")

        prepared_request = self._prepare_request(method_name=f"/validate")

        return await self._dispatch(prepared_request=prepared_request,
                                    params={'email' : email,
                                            'ip_address' : ''},
                                    command='validate_email')

    async def file_status(self, file_id):
        if not self.session:
            raise AppErrors("Call get_client_session first")

        return zb_file_status(file_id)

    async def get_file(self, payload):
        if not self.session:
            raise AppErrors("Call get_client_session first")

        file_id = payload['file_id']
        saved_path = payload['saved_path']

        return zb_get_file(file_id, saved_path)

    async def send_file(self, file_path):
        if not self.session:
            raise AppErrors("Call get_client_session first")

        return zb_send_file(file_path)

    async def _dispatch(self,
                  prepared_request,
                  command,
                        params=None,
                        req='GET'):

        request = self.session.get
        if req == 'POST':
            request = self.session.post
        elif req == 'PUT':
            request = self.session.put
        elif req == 'DELETE':
            request = self.session.delete

        settings.LOGGER.debug(f"request = {prepared_request}")
        async with request(**prepared_request, params=params) as response:
            try:
                settings.LOGGER.debug(response.request_info)
                return await self._handle_response(response)
            except Exception as e:
                traceback.print_exc()
                settings.LOGGER.error(f"..{os.path.basename(__file__)} {command}  ERROR: {str(e)}")
                raise AppErrors(f"error executin command={command} error={str(e)}")



    def _prepare_request(self,
                         method_name,
                         payload=None,
                         headers={}):
        request = {
            'url' : self.api_settings['base_url'] + method_name + f"?api_key={self.api_key}"
        }

        if payload:
            headers.update({
                'Content-Type': 'application/json'
            })
            request["data"] = payload.json()

        request["headers"] = headers

        return request

    async def _handle_response(self, response: aiohttp.ClientResponse):
        if response.status == 429:
            wait_secs = self._get_rate_limit_sleep_time(response)
            raise AppErrors(f"CloseComApiProvider exceed rate limit need to wait for {wait_secs} and try again")

        if (response.status != 200) and (response.status != 201):
            content = await response.content.read()
            raise AppErrors(f"Error request status={response.status} content={content}")

        if response.status == 204:
            return ''

        return await response.json()

    def _get_rate_limit_sleep_time(self, response: aiohttp.ClientResponse):
        try:
            data = response.json()
            rate_reset = float(data['error']['rate_reset'])
            settings.LOGGER.info(f"..rate_limit reset in={rate_reset}")
            return rate_reset
        except (AttributeError, KeyError, ValueError):
            settings.LOGGER.info(f"..rate_limit reset in=10")
            return 10
