from app.providers.closecom.api_provider import CloseComApiProvider
from app.services.closecom.service import CloseComService
from app.scripts.backend.utils import *

async def test_contact_query():
    customer_config = load_customer_config('hackernoon')
    api_provider = await CloseComApiProvider.create_api_provider(api_key=customer_config['api_key'])

    session = await api_provider.get_client_session()

    payload = {
        'emails' : ['martin@upvest.co']
    }

    async with session as s:
        res = await api_provider.execute(endpoint='leads',
                                         api_name='get_duplicates',
                                         payload=payload)
        pprint(res)

async def test_any_mongodb():
    service = CloseComService()

    leads = await service.find_leads(organization='hackernoon',
                                     internal_status='create')
    async for lead in leads:
        pprint(lead)
        if not lead.lead_id:
            print("Ura")

async def test_lead_get():
    customer_config = load_customer_config('hackernoon')
    api_provider = await CloseComApiProvider.create_api_provider(api_key=customer_config['api_key'])

    session = await api_provider.get_client_session()

    payload = {
        'lead_id' : 'lead_cbsUd4NGgK7o0Td56ykWHhNDEezg85cL6Gq9JHd86pf'
    }

    async with session as s:
        res = await api_provider.execute(endpoint='leads',
                                         api_name='get_lead',
                                         payload=payload)
        pprint(res)
