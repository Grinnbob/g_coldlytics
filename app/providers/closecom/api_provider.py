from app.core.exceptions import *
from typing import Any
from app.core.config import settings
import aiohttp
from aiohttp import BasicAuth
import traceback
import os
from app.core.config import settings
import json

from ._custom_fields import *
from ._leads import *
from ._contacts import *

API_ENDPOINTS = {
    'custom_fields' : CustomFieldsApi,
    'leads' : LeadsApi,
    'contacts' : ContactsApi
}

class CloseComApiProvider():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_api_provider to create instance")

        self.session = None

    @classmethod
    async def create_api_provider(cls,
                                  api_key,
                                  settings: dict=settings.CLOSECOM_API_SETTINGS) -> Any:

        api_provider = cls(direct=False)

        api_provider.api_settings = settings
        api_provider.api_key = api_key

        return api_provider

    async def get_client_session(self):
        if self.session:
            raise AppErrors("Session already created - use ONE session per app")

        self.session = aiohttp.ClientSession(
            auth=BasicAuth(login=self.api_key, password='')
        )

        return self.session

    async def execute(self,
                      endpoint,
                      api_name,
                      payload=None,
                      one_page=False):

        enpoint_class = API_ENDPOINTS.get(endpoint)
        if not enpoint_class:
            raise AppErrors(f"ERROR: no such endpoint = {endpoint}")

        endpoint_provider = enpoint_class(api_provider=self)

        return await endpoint_provider.run_api(api_name=api_name,
                                               payload=payload,
                                               one_page=one_page)

    async def post(self,
                   method_name,
                   payload):

        prepared_request = self._prepare_request(method_name=method_name,
                                                 payload=payload)

        return await self._dispatch(prepared_request=prepared_request,
                                    req='POST')


    async def get(self,
                  method_name,
                  one_page=None,
                  params={}):

        prepared_request = self._prepare_request(method_name=method_name,
                                                 params=params)
        if one_page is None:
            return await self._dispatch(prepared_request=prepared_request,
                                        req='GET')
        else:
            return await self._paginate(prepared_request=prepared_request,
                                        one_page=one_page)


    async def put(self,
                  method_name,
                  payload):

        prepared_request = self._prepare_request(method_name=method_name,
                                                 payload=payload)

        return await self._dispatch(prepared_request=prepared_request,
                                    req='PUT')


    ###################### REQUEST EXECTUION START HERE ############################
    async def _paginate(self,
                        prepared_request,
                        req='GET',
                        one_page=False):
        pages = []

        _skip = 0
        paginated_request = prepared_request
        while True:
            next_page = await self._dispatch(prepared_request=paginated_request,
                                             req=req)

            data = next_page.get('data', None)
            if not data:
                settings.LOGGER.error(f"There is no data in response for {prepared_request}")
                break

            received=len(data)
            settings.LOGGER.info(f"received={received} skip={_skip}  limit={settings.CLOSECOM_PAGE_LIMIT}")

            pages.extend(data)

            if one_page:
                settings.LOGGER.info(f"BREAK on once: one_page={one_page}")
                break

            has_more = next_page.get('has_more', False)
            if not has_more:
                break

            _skip = _skip + received
            paginated_request = self._next_page(prepared_request, _skip)

        return pages

    def _next_page(self,
                   prepared_request,
                   _skip):

        url = prepared_request.get('url', None)
        if not url:
            raise Exception(f"Wrong prepared_request, not url ={prepared_request}")


        url = url + f"?_skip={_skip}&_limit={settings.CLOSECOM_PAGE_LIMIT}"

        paginated_request = prepared_request.copy()
        paginated_request['url'] = url

        return paginated_request


    #Construct dict to pass to aiohttp.session.method(..)
    def _prepare_request(self,
                         method_name,
                         params={},
                         payload=None,
                         headers={}):
        request = {
            'url' : self.api_settings['base_url'] + method_name
        }

        if payload:
            headers.update({
                'Content-Type': 'application/json'
            })
            request["data"] = json.dumps(payload)

        if params:
            request["params"] = params

        request["headers"] = headers

        return request


    #params - get parameters
    #prepared_request - dict that contact request parameters
    async def _dispatch(self,
                        prepared_request,
                        req='GET'):

        request = self.session.get
        if req == 'POST':
            request = self.session.post
        elif req == 'PUT':
            request = self.session.put
        elif req == 'DELETE':
            request = self.session.delete

        settings.LOGGER.debug(f"request = {prepared_request}")
        async with request(**prepared_request) as response:
            try:
                settings.LOGGER.debug(response.request_info)
                return await self._handle_response(response)
            except Exception as e:
                traceback.print_exc()
                settings.LOGGER.error(f"..{os.path.basename(__file__)}  ERROR: {str(e)}")
                raise AppErrors(f"error executing request={prepared_request} error={str(e)}")


    async def _handle_response(self, response: aiohttp.ClientResponse):
        if response.status == 429:
            wait_secs = self._get_rate_limit_sleep_time(response)
            raise AppErrors(f"CloseComApiProvider exceed rate limit need to wait for {wait_secs} and try again")

        if (response.status != 200) and (response.status != 201):
            content = await response.content.read()
            raise AppErrors(f"Error request status={response.status} content={content}")

        if response.status == 204:
            return ''

        response = await response.json()

        settings.LOGGER.debug(f"...response = {response}")
        return response

    def _get_rate_limit_sleep_time(self, response: aiohttp.ClientResponse):
        try:
            data = response.json()
            rate_reset = float(data['error']['rate_reset'])
            settings.LOGGER.info(f"..rate_limit reset in={rate_reset}")
            return rate_reset
        except (AttributeError, KeyError, ValueError):
            settings.LOGGER.info(f"..rate_limit reset in=10")
            return 10
