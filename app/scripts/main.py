import argparse
import asyncio
import uvloop
from app.core.config import settings
from app.core.exceptions import *

from app.scripts.backend.clients import *
from app.scripts.backend.spreadsheet_checker import *
from app.scripts.backend.spreadsheet_uploader import *
from app.scripts.zerobounce.check import *
from app.scripts.zerobounce.credits import *
from app.scripts.fortest import *

async_actions = {
    'create_customer' : create_customer,
    'setup_customer' : setup_customer,
    'create_drive' : create_drive,
    'delete_drive' : delete_drive,

    'check_leads' : check_leads,
    'show_all_checks' : show_all_checks,
    'create_leads_check' : create_leads_check,
    'launch_leads_check' : launch_leads_check,
    'leads_ready_download' : leads_ready_download,
    'leads_update_spreadsheet' : leads_update_spreadsheet,
    'revert_spreadsheet_update' : revert_spreadsheet_update,

    'zb_show_credits' : zb_credits,
    'zb_file_status' : zb_file_status,
    'zb_get_file' : zb_get_file,

    'create_leads' : create_leads,
    'update_leads' : update_leads,
    'upload_leads' : upload_leads,
    'update_custom_fields' : update_custom_fields,
    'create_missing_custom_fields' : create_missing_custom_fields,


    'test' : test,
}


async def dispatch(args):
    if args.create_customer:
        return await async_actions['create_customer'](args.create_customer)
    elif args.setup_customer:
        return await async_actions['setup_customer'](args.setup_customer)
    elif args.create_drive:
        return await async_actions['create_drive'](args.create_drive)
    elif args.delete_drive:
        return await async_actions['delete_drive'](args.delete_drive)

    elif args.zb_show_credits:
        return await async_actions['zb_show_credits']()
    elif args.zb_file_status:
        return await async_actions['zb_file_status'](args.zb_file_status)
    elif args.zb_get_file:
        return await async_actions['zb_get_file'](args.zb_get_file)

    elif args.check_leads:
        return await async_actions['check_leads'](args.check_leads[0],
                                                  args.check_leads[1])
    elif args.create_leads:
        return await async_actions['create_leads'](args.create_leads)
    elif args.update_leads:
        return await async_actions['update_leads'](args.update_leads)
    elif args.upload_leads:
        return await async_actions['upload_leads'](args.upload_leads)
    elif args.update_all_custom_fields:
        return await async_actions['update_custom_fields'](args.update_all_custom_fields)
    elif args.create_missing_custom_fields:
        return await async_actions['create_missing_custom_fields'](args.create_missing_custom_fields)

    elif args.show_all_checks:
        return await async_actions['show_all_checks'](args.show_all_checks)
    elif args.create_leads_check:
        return await async_actions['create_leads_check'](args.create_leads_check[0],
                                                         args.create_leads_check[1])
    elif args.launch_leads_check:
        return await async_actions['launch_leads_check'](args.launch_leads_check)
    elif args.leads_ready_download:
        return await async_actions['leads_ready_download'](args.leads_ready_download)
    elif args.leads_update_spreadsheet:
        return await async_actions['leads_update_spreadsheet'](args.leads_update_spreadsheet)
    elif args.revert_spreadsheet_update:
        return await async_actions['revert_spreadsheet_update'](args.revert_spreadsheet_update)

    elif args.test:
        return await async_actions['test'](args.test)
    else:
        print("usage: prog [OPTION] [PARAMETER]")
        return

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(usage="%(prog)s [OPTION] [PARAMETER]...",
                                     description="coldlytics console interface",
                                     )
    parser.add_argument("--test",
                        help="<param> call test with param from fortest",
                        type=str)

    parser.add_argument("--create-customer",
                        help="<name> create directory with config template",
                        type=str)
    parser.add_argument("--setup-customer",
                        help="<name> execute all setup operations: drive, close for a customer",
                        type=str)
    parser.add_argument("--create-drive",
                        help="<name> setup google drive folder and files for a customer",
                        type=str)
    parser.add_argument("--delete-drive",
                        help="<name> setup google drive folder and files for a customer",
                        type=str)


    parser.add_argument("--zb-file-status",
                        help="<key> show status for file_id",
                        type=str)
    parser.add_argument("--zb-show-credits",
                        help="show the current credits balance at zerobounce",
                        action="store_true")
    parser.add_argument("--zb-get-file",
                        help="<key> get file from zerobounce",
                        type=str)

    parser.add_argument("--create-leads",
                        help="<name> download spreadsheet to database will not update existing or missing data",
                        type=str)
    parser.add_argument("--update-leads",
                        help="<name> download spreadsheet to database and update the leads",
                        type=str)
    parser.add_argument("--upload-leads",
                        help="<name> will upload new and updated leads to spreadsheet_uploader",
                        type=str)
    parser.add_argument("--update-all-custom-fields",
                        help="<name> will update custom fields for leads and contacts in DB",
                        type=str)
    parser.add_argument("--create-missing-custom-fields",
                        help="<name> will upload config and create missing custom fields",
                        type=str)


    parser.add_argument("--check-leads",
                        help="<name | renew> create and launch leads check for the customer",
                        nargs=2,
                        type=str)
    parser.add_argument("--create-leads-check",
                        help="<name | renew> create check for customer",
                        nargs=2,
                        type=str)
    parser.add_argument("--launch-leads-check",
                        help="<name> create check for customer",
                        type=str)
    parser.add_argument("--leads-ready-download",
                        help="<name> download all tested checks from zerobounce",
                        type=str)
    parser.add_argument("--show-all-checks",
                        help="<name> show all lead checks for customer",
                        type=str)
    parser.add_argument("--leads-update-spreadsheet",
                        help="<name> update spreadsheet for the customer",
                        type=str)
    parser.add_argument("--revert-spreadsheet-update",
                        help="<key> will revert status to checked and allow to launch sheet update again",
                        type=str)

    return parser


def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(dispatch(args))

if __name__ == '__main__':
    main()