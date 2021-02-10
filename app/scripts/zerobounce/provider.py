from app.providers.zerobounce.zerobounce_api import ZerobounceApiProvider

async def _execute_zerobounce_api(api_name, payload=None):
    api_provider = await ZerobounceApiProvider.create_api_provider()

    api_session = await api_provider.get_client_session()
    async with api_session as session:
        api_method = getattr(api_provider, api_name)
        data = {}
        if payload:
            data = await api_method(payload)
        else:
            data = await api_method()

        return data

    return None