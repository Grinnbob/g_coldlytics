from pathlib import Path
import os
import json
from app.core.exceptions import *
from app.core.config import settings
from pprint import pprint
from .utils import *
from app.providers.google.gspread_api import GspreadProvider
import app.scripts.zerobounce.check as zcheck
#check leads in the spreadsheet
import traceback
from validate_email import validate_email
import pandas as pd
from app.services.zerobounce.service import ZeroBounceService
from pprint import pprint
import time
from datetime import datetime

async def show_all_checks(customer):
    config_data = load_customer_config(customer)
    name = config_data['name']

    checks = await zcheck.zb_customer_checks(name)
    if not checks:
        print(f"NO CHECKS: for organization={customer}")
        return

    for check in checks:
        print(f"CHECK: | organization={check['organization']} | status={check['status']} | sheet_title={check.get('meta_desc', {}).get('sheet_title', 'NONE')} | key={check.get('key')}")

    print(f"raw data:")
    pprint(checks)

async def check_leads(customer, renew):
    await create_leads_check(customer, renew)
    await launch_leads_check(customer)
    print(f"SUCCESS: leads uploaded to zerobounce for organization={customer} renew={renew}")

    print(f"...waiting for file ready")
    await leads_ready_download(customer)

    print(f"...updating spreadsheet")
    await leads_update_spreadsheet(customer)

async def revert_spreadsheet_update(key):
    zb_service = ZeroBounceService()
    return await zb_service.change_status(key, 'checked')

async def leads_update_spreadsheet(customer):
    config_data = load_customer_config(customer)
    customer_name = config_data['name']

    leads_url = config_data['leads_spreadsheet']
    if not leads_url:
        raise AppErrors(f"EMPTY URL: lead spreadsheet url empty url={leads_url}")

    gspread_provider = await GspreadProvider.create_api_provider()
    spreadsheet = await gspread_provider.open(leads_url)
    if not spreadsheet:
        raise AppErrors(f"OPEN ERROR: can't open spreadsheet={leads_url}  res={spreadsheet}")

    work_sheets = await gspread_provider.worksheets()
    if not work_sheets:
        raise AppErrors(f"NO WORKSHEETS: no worksheets found for spreadsheet={leads_url}")

    zb_service = ZeroBounceService()
    updated = 0
    while True:
        cursor = await zb_service.get_checked_checks(customer_name)
        empty = True
        async for check in cursor:
            updated += 1
            empty = False
            try:
                res = await _mark_invalid_emails(gspread_provider=gspread_provider,
                                           work_sheets=work_sheets,
                                           check=check,
                                            client_config=config_data)
                if res:
                    await zb_service.sheet_updated(check.key)

                    meta_desc = check.meta_desc
                    sheet_title = meta_desc.get('sheet_title', 'no_title')
                    print(f"SUCCESS: updated for sheet_tile={sheet_title} key={check.key}")

            except Exception as e:
                print(f"ERROR: updating sheet for: key={check.key} error={str(e)}")
        if empty:
            break

    if not updated:
        print(f"NOTHING to update")

    return

async def leads_ready_download(customer):
    config_data = load_customer_config(customer)
    customer_name = config_data['name']

    zb_service = ZeroBounceService()

    secs = 16
    i = 0
    while True:
        cursor = await zb_service.get_inprogress_checks(customer_name)
        empty = True
        skip_waiting = False
        async for check in cursor:
            empty = False
            try:
                status = await zcheck.zb_file_status(check.key)
                if str(status).lower() == 'complete':
                    res = await zcheck.zb_get_file(check.key)
                    skip_waiting = True
            except Exception as e:
                print(f"ERROR download: organization={customer_name} key={check.key} error={str(e)}")
                continue
        if empty:
            break

        i += 1
        if not skip_waiting:
            print(f"{i} ...waiting {secs} secconds")
            time.sleep(secs)
            secs *= 2

    print(f"FINISHED {i} steps...")
    return


async def launch_leads_check(customer):
    config_data = load_customer_config(customer)
    customer_name = config_data['name']

    zb_service = ZeroBounceService()
    cursor = await zb_service.get_new_checks(customer_name)

    empty = True
    async for check in cursor:
        empty = False
        try:
            await zcheck.zb_launch_check(check.key)
        except Exception as e:
            print(f"ERROR launch: organization={customer_name} key={check.key} error={str(e)}")
            continue

    if empty:
        print(f"NO CHECKS: nothing to launch for organization={customer_name}")

    return

async def create_leads_check(customer, renew):
    if renew == 'renew':
        renew = True
    else:
        renew = False

    config_data = load_customer_config(customer)
    customer_name = config_data['name']

    leads_url = config_data['leads_spreadsheet']
    if not leads_url:
        raise AppErrors(f"EMPTY URL: lead spreadsheet url empty url={leads_url}")

    gspread_provider = await GspreadProvider.create_api_provider()
    spreadsheet = await gspread_provider.open(leads_url)
    if not spreadsheet:
        raise AppErrors(f"OPEN ERROR: can't open spreadsheet={leads_url}  res={spreadsheet}")

    data_sheets = []
    work_sheets = await gspread_provider.worksheets()
    if not work_sheets:
        raise AppErrors(f"NO WORKSHEETS: no worksheets found for spreadsheet={leads_url}")
    else:
        print(f"...found {len(work_sheets)} sheets, reading data:")
        for sheet in work_sheets:
            print(f"reading tab: {sheet.title}")
            miss = str(input("Do you want to skip this tab? (N/y)") or 'n')
            if miss.lower() == "y":
                continue

            email_header_cell = 0
            while not email_header_cell:
                email_header_cell = str(input("Email header cell? (A1, I22, ..)"))

            data_sheets.append(_load_sheet_meta(spreadsheet=spreadsheet,
                                                sheet=sheet,
                                                email_header_cell=email_header_cell.lower()))
    for sheet_meta in data_sheets:
        await _create_check(provider=gspread_provider,
                            sheet_meta=sheet_meta,
                            customer=customer_name,
                            renew=renew)

    return

async def _mark_invalid_emails(gspread_provider,
                               work_sheets,
                               check,
                               client_config):
    sheet_id = get_sheet_id_from_key(check.key)

    sheet_to_update = None
    for sheet in work_sheets:
        if sheet_id == str(sheet.id):
            sheet_to_update = sheet
            break

    if not sheet_to_update:
        raise AppErrors(f"There is no sheet found for key={check.key} sheet_id={sheet_id}")

    email_data = json.loads(check.email_data)

    invalid_emails, stats = _calc_email_data(email_data,
                                             client_config['valid_leads'])

    if invalid_emails:
        cells = await gspread_provider.find_invalid_cells(sheet_to_update, invalid_emails)
        if cells:
            await gspread_provider.mark_invalid_cells(sheet_to_update, cells, invalid_emails)

    await gspread_provider.update_stats(sheet_to_update, stats)

    return True

def _calc_email_data(email_data,
                     accept_list):
    invalid_emails = {}
    stats = {
        '' : '',
        'utc check date' : str(datetime.utcnow()),
        'valid statuses' : ",".join(accept_list),
        'catch_all_emails' : 0,
        'unique_emails' : 0,
        'invalid_emails' : 0,
        'valid_emails' : 0,
        'invalid_rate' : 0,
        'catch_all_rate' : 0
    }

    for email, status in email_data.items():
        stats['unique_emails'] += 1
        if status not in accept_list:
            stats['invalid_emails'] += 1
        else:
            stats['valid_emails'] += 1

        if status == 'catch-all':
            stats['catch_all_emails'] += 1

        if status != 'valid':
            invalid_emails[email] = status

    if stats['unique_emails'] > 0:
        stats['invalid_rate'] = round(stats['invalid_emails']/stats['unique_emails'], 2)
        stats['catch_all_rate'] = round(stats['catch_all_emails']/stats['unique_emails'], 2)

    return invalid_emails, stats

async def _create_check(
        customer,
        provider,
        sheet_meta,
        renew=False):
    key = create_chek_key(spreadsheet_id=sheet_meta['spreadsheet_id'],
                          sheet_id=sheet_meta['sheet_id'])

    emails = await _load_emails(provider=provider,
                                sheet_meta=sheet_meta)

    if emails == -1:
        print(f"SKIP DATA: you can try again later {sheet_meta['sheet_title']}")
        return None

    try:
        meta_desc = _create_meta_desc(sheet_meta)
        await zcheck.zb_create_check(key=key,
                                     emails=emails,
                                     customer=customer,
                                     meta_desc=meta_desc,
                                     renew=renew)
        print(f"CHECK CREATED: sheet_title={sheet_meta['sheet_title']}  key={key}")
    except Exception as e:
        if hasattr(e, 'message') and 'CHECK EXIST' in e.message:
            print(f"SKIPPING CHECK: check exist sheet_title={sheet_meta['sheet_title']} key={key}")
        else:
            traceback.print_exc()
            raise AppErrors(str(e))

async def _load_emails(
        provider,
        sheet_meta):

    col, row = _conver_to_col_row(sheet_meta['email_header_cell'])

    sheet = sheet_meta['sheet']
    df = await provider.load_column(sheet=sheet,
                                    column=col,
                                    start_row=row)

    valid_emails = df[df.columns[0]].apply(lambda x: str(x).strip() if validate_email(str(x).strip()) else None).dropna()
    print(valid_emails)
    agree = input("Is that ok? y/n: ")
    if agree.lower() == 'n':
        return -1

    if valid_emails is None:
        return -1

    emails = valid_emails.values.tolist()
    return emails

def _conver_to_col_row(cell_title):
    letter = cell_title[0].lower()
    col = SHEET_COLS[letter]
    row = int(cell_title[1:])

    return col, row


def _create_meta_desc(sheet_meta):
    res = sheet_meta.copy()

    del res['sheet']
    del res['spreadsheet']
    return res

def _load_sheet_meta(spreadsheet,
                    sheet,
                     email_header_cell):
    return dict(spreadsheet_id=spreadsheet.id,
                sheet_id=sheet.id,
                sheet_title=sheet.title,
                email_header_cell=email_header_cell,
                sheet=sheet,
                spreadsheet=spreadsheet)