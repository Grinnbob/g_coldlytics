from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import secrets
from typing import Optional, Dict, Any, Union
from pathlib import Path
import json
import os
import logging

class Settings(BaseSettings):
    ENVIRONMENT: str = ''
    PROJECT_NAME: str = 'theclone'
    API_V1_STR: str = "/api/v1"

    #faust
    FAUST_APP_NAME: str = 'theclone_stream_app'
    FAUST_APP_BROKER: str
    FAUST_APP_STORE: str

    #topics
    TOPIC_LIST_CHANGE: str
    TOPIC_MESSAGE_CHANGE: str

    #Push/Pull updates
    PULL_GOOGLE_PERIOD: int
    GOOGLE_PUB_SUB_TOPIC: str
    GOOGLE_PUB_SUB_SUBSCRIPTION_NAME: str
    GOOGLE_PUB_SUB_MAX_MESSAGES: int

    #gmail ADDON
    ADDON_CLIENT_ID: str

    #UX/UI
    PER_PAGE: int = 20

    #System
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = ''
    SECRET_KEY: str = ''

    @validator("SECRET_KEY", pre=True)
    def secret_key_check(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if not v:
            raise ValueError("SECRET_KEY can't be empty")

        return v

    @validator("ACCESS_TOKEN_EXPIRE_MINUTES", pre=True)
    def token_expire_check(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if int(v) < 10080:
            raise ValueError(f"ACCESS_TOKEN_EXPIRE_MINUTES is too small {v}")

        return v


    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = ''

    LIST_SYNC_PRODUCER_PERIOD: int = 120
    GET_SYNC_PRODUCER_PERIOD: int = 120
    MAX_ACTIVE_LISTS:int = 1000000

    MSG_BATCH_SIZE: int = 0
    NEXT_PAGE_ITER_COUNT: int = 0

    #GOOGLE OAUTH
    GOOGLE_OAUTH_MAJOR_REDIRECT_URL:str = ''
    GOOGLE_OAUTH_ADDON_REDIRECT_URL:str = ''

    GOOGLE_GMAIL_API_PUSH_TOPIC:str = ''
    GOOGLE_CREDENTIALS_FILENAME:str = ''
    GOOGLE_REDIRECT_URI:str = ''
    GOOGLE_GMAIL_SCOPES: Optional[list] = ['']
    GOOGLE_GMAIL_ACCESS_TYPE:str = ''
    GOOGLE_GMAIL_INCLUDE_GRANTED_SCOPES:str = ''
    GOOGLE_GMAIL_API_NAME:str = ''
    GOOGLE_GMAIL_API_VERSION:str = ''

    GOOGLE_CLIENT_SETTINGS: dict = {}

    @validator("GOOGLE_CLIENT_SETTINGS")
    def assemble_google_settings(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        if isinstance(v, dict) and v:
            return v

        credentials = {}
        path = Path(__file__).parent / f'../_data/{values.get("GOOGLE_CREDENTIALS_FILENAME")}'
        with path.open() as f:
            creds = json.load(f)
            if creds.get('web'):
                credentials['credentials'] = creds.get('web')
            else:
                credentials['credentials'] = creds

        if not credentials:
            raise ValueError(credentials)

        credentials['redirect_uri'] = values.get('GOOGLE_REDIRECT_URI')
        credentials['gmail_scopes'] = values.get('GOOGLE_GMAIL_SCOPES')
        credentials['gmail_access_type'] = values.get('GOOGLE_GMAIL_ACCESS_TYPE')
        credentials['gmail_include_granted_scopes'] = values.get('GOOGLE_GMAIL_INCLUDE_GRANTED_SCOPES')
        credentials['gmail_api_name'] = values.get('GOOGLE_GMAIL_API_NAME')
        credentials['gmail_api_version'] = values.get('GOOGLE_GMAIL_API_VERSION')

        if values.get('ENVIRONMENT') == 'dev':
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        return credentials

    GOOGLE_GDRIVE_ROOT_FOLDER: str
    GOOGLE_GDRIVE_ROOT_FOLDER_ID: str
    GOOGLE_DRIVE_LEADS_TEMPLATE_ID: str
    GOOGLE_DRIVE_STATS_TEMPLATE_ID: str
    GOOGLE_GDRIVE_API_NAME: str
    GOOGLE_GDRIVE_API_VERSION: str
    GOOGLE_GDRIVE_SCOPES: Optional[list] = ['']

    GOOGLE_SERVICE_ACCOUNT_KEY_FILENAME: str
    GOOGLE_SERVICE_ACCOUNT_SETTINGS: dict = {}

    @validator("GOOGLE_SERVICE_ACCOUNT_SETTINGS")
    def assemble_google_service_account_settings(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        if isinstance(v, dict) and v:
            return v

        credentials = {}
        path = Path(__file__).parent / f'../_data/{values.get("GOOGLE_SERVICE_ACCOUNT_KEY_FILENAME")}'
        with path.open() as f:
            creds = json.load(f)
            credentials['credentials'] = creds

        if not credentials:
            raise ValueError(credentials)

        credentials['gdrive_scopes'] = values.get('GOOGLE_GDRIVE_SCOPES')
        credentials['gdrive_api_name'] = values.get('GOOGLE_GDRIVE_API_NAME')
        credentials['gdrive_api_version'] = values.get('GOOGLE_GDRIVE_API_VERSION')
        credentials['gdrive_root_folder'] = values.get('GOOGLE_GDRIVE_ROOT_FOLDER')
        credentials['gdrive_root_folder_id'] = values.get('GOOGLE_GDRIVE_ROOT_FOLDER_ID')
        credentials['gdrive_leads_template_id'] = values.get('GOOGLE_DRIVE_LEADS_TEMPLATE_ID')
        credentials['gdrive_stats_template_id'] = values.get('GOOGLE_DRIVE_STATS_TEMPLATE_ID')


        return credentials



    PUB_SUB_KEY_FILENAME: str
    PUB_SUB_KEY: dict = {}
    PUB_SUB_CREDENTIALS_AUDIENCE: str

    @validator("PUB_SUB_KEY")
    def assemble_pub_sub(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        if isinstance(v, dict) and v:
            return v

        data = {}

        path = Path(__file__).parent / f'../_data/{values.get("PUB_SUB_KEY_FILENAME")}'
        with path.open() as f:
            data = json.load(f)

        if not data:
            raise ValueError(data)

        return data

    MONGODB_HOST:str
    MONGODB_PORT:int
    MONGODB_DB_NAME:str
    MONGODB_MAX_CONNECTIONS_COUNT:int
    MONGODB_MIN_CONNECTIONS_COUNT:int

    MONGODB_URI: Optional[str] = None

    @validator("MONGODB_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v is not None:
            return v

        url = f'mongodb://{values["MONGODB_HOST"]}:{values["MONGODB_PORT"]}/{values["MONGODB_DB_NAME"]}'
        return url

    class Config:
        env_file = Path(__file__).parent / '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True

    CLOSECOM_PAGE_LIMIT: int
    CLOSECOM_API_CREDENTIALS: str = ''
    CLOSECOM_API_SETTINGS: dict = {}
    PULL_CLOSECOM_PERIOD: int

    @validator("CLOSECOM_API_SETTINGS")
    def assemble_closecom_settings(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        if isinstance(v, dict) and v:
            return v

        credentials = {}
        path = Path(__file__).parent / f'../_data/{values.get("CLOSECOM_API_CREDENTIALS")}'
        with path.open() as f:
            creds = json.load(f)

            credentials['base_url'] = creds.get('base_url')
            credentials['api_key'] = creds.get('api_key')

        if not credentials:
            raise ValueError(credentials)

        return credentials


    ZEROBOUNCE_API_CREDENTIALS: str = ''
    ZEROBOUNCE_API_SETTINGS: dict = {}
    PULL_ZEROBOUNCE_PERIOD: int

    @validator("ZEROBOUNCE_API_SETTINGS")
    def assemble_zerobounce_settings(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        if isinstance(v, dict) and v:
            return v

        credentials = {}
        path = Path(__file__).parent / f'../_data/{values.get("ZEROBOUNCE_API_CREDENTIALS")}'
        with path.open() as f:
            creds = json.load(f)

            credentials['base_url'] = creds.get('base_url')
            credentials['bulk_base_url'] = creds.get('bulk_base_url')
            credentials['api_key'] = creds.get('api_key')

        if not credentials:
            raise ValueError(credentials)

        return credentials

    NLP_PROVIDER_SETTINGS = ''

    LOGGING_LEVEL: str = ''
    LOGGER: str = None

    @validator("LOGGER")
    def set_logger(cls, v: Optional[dict], values: Dict[str, Any]) -> Any:
        #logger = logging.getLogger('app_logger')

        level = values.get("LOGGING_LEVEL")
        if not level:
            raise ValueError("Setup LOGGING_LEVEL")

        if level == 'DEBUG':
            logging.basicConfig(level=logging.DEBUG)
        elif level == 'INFO':
            logging.basicConfig(level=logging.INFO, format='%(message)s')
        elif level == 'WARNING':
            logging.basicConfig(level=logging.WARNING)
        elif level == 'ERROR':
            logging.basicConfig(level=logging.ERROR)
        elif level == 'CRITICAL':
            logging.basicConfig(level=logging.CRITICAL)
        else:
            raise ValueError(f"Unknow logger level={level} should be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")

        return logging



settings = Settings()

#settings = Settings(_env_file=Path(__file__).parent / '.prod.env', _env_file_encoding='utf-8')

#Production settings
