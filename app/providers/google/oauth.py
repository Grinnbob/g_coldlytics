from app.core.exceptions import *
from app.core.config import settings
import google_auth_oauthlib.flow

class GoogleOauthProvider():
    def __init__(self, settings=settings.GOOGLE_CLIENT_SETTINGS):
        self.setting = settings

    def get_gmail_auth_url(self, current_state):
        scopes = self.settings.gmail_scopes
        access_type = self.settings.gmail_access_type
        include_granted_scopes = self.settings.gmail_include_granted_scopes

        flow = self._get_flow(scopes,
                              current_state)

        auth_url, state = flow.authorization_url(
            access_type=access_type,
            prompt='consent',
            include_granted_scopes=include_granted_scopes)

        return auth_url, state

    def fetch_token(self, request_url, current_state):
        scopes = self.settings.gmail_scopes

        flow = self._get_flow(scopes,
                              current_state)

        flow.fetch_token(authorization_response=request_url)

        if not flow.credentials:
            raise AppErrors("flow.fetch_token error")

        access_credentials = self.credentials_to_dict(flow.credentials)
        expiry = flow.credentials.expiry

        return access_credentials, expiry

    @classmethod
    def credentials_to_dict(cls, flow_credentials):
        return {'token': flow_credentials.token,
                'refresh_token': flow_credentials.refresh_token,
                'token_uri': flow_credentials.token_uri,
                'client_id': flow_credentials.client_id,
                'client_secret': flow_credentials.client_secret,
                'scopes': flow_credentials.scopes}

    @classmethod
    def valid_state(cls, state, current_state):
        if state != current_state:
            return False

        return True

    def _get_flow(self, scopes, state):
        credentials = self.settings.credentials
        redirect_uri = self.settings.redirect_uri

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            credentials,
            scopes=scopes,
            state=state)

        flow.redirect_uri = redirect_uri

        return flow
