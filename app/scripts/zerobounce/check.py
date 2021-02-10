from app.core.config import settings
from app.core.exceptions import *
from app.scripts.zerobounce.provider import _execute_zerobounce_api
from app.services.zerobounce.service import ZeroBounceService
from app.providers.zerobounce.zerobounce_api import ZerobounceApiProvider
from pprint import pprint
import uuid
import traceback
from pathlib import Path
from app.files.zerobounce import zb_files_directory
from app.files.zerobounce.checked import zb_download_directory
import pandas as pd

TEST_EMAILS = [
    "disposable@example.com",
    "invalid@example.com",
    "valid@example.com",
]
#To launch check we need:
# 1. Call zb_create_check - will create check in database (return the key)
# 2. Call zb_launch_check - will create the file if not exist, and send file to Zerobounce API.

async def zb_customer_checks(name):
    zb_service = ZeroBounceService()

    cursor = await zb_service.get_organization_checks(name)

    checks = []
    async for check in cursor:
        checks.append(dict(key=check.key,
                           status=check.status,
                           organization=check.organization,
                           meta_desc=check.meta_desc,
                           file_id=check.file_id,
                           file_name=check.file_name))

    return checks


async def zb_get_file(key):
    zb_service = ZeroBounceService()

    check = await zb_service.get(key)
    if not check:
        raise AppErrors(f"NOT FOUND: check for key={key}")

    file_id = check.file_id
    if not file_id:
        raise AppErrors(f"NO FILE_ID: there is no file_id for key={key}, call --zb-launch-check first")

    saved_path = zb_download_directory / f'{key}.csv'
    payload = {
        'file_id' : file_id,
        'saved_path' : saved_path
    }
    res = await _execute_zerobounce_api("get_file", payload)

    data = pd.read_csv(saved_path)
    serialized_data = _convert_to_normal_dict(data)

    await zb_service.checked(file_id, serialized_data)

    print(f"SUCCESS: file received and stored = {res}")

async def zb_file_status(key):
    zb_service = ZeroBounceService()

    check = await zb_service.get(key)
    if not check:
        raise AppErrors(f"NOT FOUND: check for key={key}")

    file_id = check.file_id
    if not file_id:
        raise AppErrors(f"NO FILE_ID: there is no file_id for key={key}, call --zb-launch-check first")

    res = await _execute_zerobounce_api("file_status", file_id)

    print(f"SUCCESS: {res.file_status} for key={key} file_id={file_id}")
    settings.LOGGER.debug(res)

    return res.file_status

async def zb_create_check(key,
                          emails,
                          customer='system',
                          meta_desc={},
                          renew=False):
    zb_service = ZeroBounceService()

    need_credits = await zb_service.create_check(key=key,
                                                 emails=emails,
                                                 organization=customer,
                                                 meta_desc=meta_desc,
                                                 renew=renew)

    if need_credits == 0:
        print(f"zerobounce check ready with key={key} customer={customer}")
        return key

    has_credits = await _execute_zerobounce_api("get_credits")

    print(f"SUCCESS: zerobounce check created with key={key}, Credits on BALANCE={has_credits}  need_credits={need_credits} customer={customer}")
    return key

async def zb_launch_check(key):
    zb_service = ZeroBounceService()

    status = await zb_service.get_status(key)
    if status == 'inprogress':
        raise AppErrors(f"ALREADY IN PROGRESS: check is in progress for key={key} status={status}")
    elif status == 'checked' or status == 'sheet_updated':
        raise AppErrors(f"ALREADY CHECKED: check is checked for key={key} status={status}")

    # get data for check
    for_check = await zb_service.get_for_check(key)
    if not for_check:
        raise AppErrors(f"NO EMAILS: for_check empty for key={key}")

    #create file if not exist
    file_name = _zb_create_file(key, for_check)
    file_id = None
    res = None
    try:
        file_path = zb_files_directory / file_name
        res = await _execute_zerobounce_api("send_file", file_path)
        if not res:
            raise AppErrors(f"SEND_FILE response error: res={res}")

        if not res.success:
            raise AppErrors(f"SEND_FILE response error: res={res}")

        file_id = res.file_id
    except Exception as e:
        _zb_delete_file(file_name)
        traceback.print_exc()
        print(res)
        raise AppErrors(str(e))

    #save check to database
    await zb_service.launched(key=key,
                              file_id=file_id,
                              file_name=file_name)

    print(f"SUCCESS: file check launched for file_id={file_id}  key={key} file_path={file_path} res={res}")
    return file_id


def _zb_create_file(key, data):
    file_name = f'{key}.csv'
    file_path = zb_files_directory / file_name

    df = pd.DataFrame(data, columns=['email'])
    df.to_csv(file_path, index=False, header=True)

    return file_name

def _zb_delete_file(file_name):
    file_path = zb_files_directory / file_name

    file_path.unlink(missing_ok=True)

def _convert_to_normal_dict(data):
    return data.to_dict('records')
