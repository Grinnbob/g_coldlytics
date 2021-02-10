from app.core.exceptions import *
from typing import Any
from app.services.base_service import CLBaseService
from .models import *
import json

class ZeroBounceService(CLBaseService):
    def __init__(self):
        super().__init__()

    async def get_checked_checks(self,
                                 organization):
        return ZBCheck.find({'organization' : organization, 'status' : 'checked'})

    async def get_inprogress_checks(self,
                                    organization):
        return ZBCheck.find({'organization' : organization, 'status' : 'inprogress'})

    async def get_new_checks(self,
                             organization):
        return ZBCheck.find({'organization' : organization, 'status' : 'new'})

    async def get_organization_checks(self,
                                      organization):
        return ZBCheck.find({'organization' : organization}, {'for_check' : 0, 'email_data' : 0, 'response' : 0})

    async def get(self,
                  key):
        return await ZBCheck.find_one({'key' : key})

    async def get_checked(self,
                          key):
        return await ZBCheck.find_one({'key' : key, 'status' : 'checked'})

    async def get_status(self,
                         key):
        exist = await ZBCheck.find_one({'key' : key})
        if not exist:
            raise AppErrors(f"Check doesn't exist for key={key}")

        return exist.status

    async def change_status(self,
                            key,
                            status):
        collection = ZBCheck.collection
        return await collection.update_one({'key' : key},{
            '$set' : {
                'status' : status
            }
        })

    async def sheet_updated(self,
                            key):
        collection = ZBCheck.collection
        return await collection.update_one({'key' : key},{
            '$set' : {
                'status' : 'sheet_updated'
            }
        })

    async def launched(self,
                       key: str,
                       file_id: str,
                       file_name: str):
        collection = ZBCheck.collection
        return await collection.update_one({'key' : key},{
            '$set' : {
                'file_id' : file_id,
                'file_name' : file_name,
                'status' : 'inprogress'
            }
        })

    async def get_for_check(self,
                            key):
        check = await ZBCheck.find_one({'key' : key})
        if not check:
            raise AppErrors(f"NOT FOUND: key={key} doesn't exist")

        return check['for_check']

    async def checked(self,
                      file_id: str,
                      results: list):

        check = await ZBCheck.find_one({'file_id' : file_id})
        if not check:
            raise AppErrors(f"NOT FOUND: check for file_id={file_id} doesn't exist")


        email_data = json.loads(check['email_data'])
        checked_emails = []
        for next_email in results:
            email = str(next_email.get('email')).strip().lower()
            status = next_email.get('ZB Status')

            email_data[email] = status
            checked_emails.append(dict(email=email,
                                  status=status,
                                  zb_response=next_email))

        check.response = results
        check.email_data = json.dumps(email_data)
        check.status = "checked"

        await check.commit()
        await check.reload()

        await self._update_email_store(checked_emails)

        return check

    async def create_check(self,
                           organization: str,
                           key: str,
                           emails: list,
                           meta_desc = {},
                           renew=False) -> Any:
        exist = await ZBCheck.find_one({'key' : key})
        if exist and not renew:
            raise AppErrors(f"CHECK EXIST: key={key} status={exist['status']}")

        if not emails:
            raise AppErrors(f"NO DATA: emails can't be empty")

        emails = [str(e).strip().lower() for e in emails]

        for_check = set(emails)
        email_data = dict.fromkeys(list(for_check), "not_checked")

        zb_emails = ZBEmail.find({'email' : {'$in' : emails}})
        async for row in zb_emails:
            email = row.email
            status = row.status

            email_data[email] = status
            try:
                for_check.remove(email)
            except:
                pass

        need_credits = len(for_check)

        status = "new"
        if need_credits == 0:
            status = "checked"

        email_data = json.dumps(email_data)
        for_check = list(for_check)
        if not renew:
            check = ZBCheck(
                organization=organization,
                meta_desc=meta_desc,
                key=key,
                status=status,
                for_check = for_check,
                email_data = email_data
            )

            await check.commit()
        elif renew == True:
            collection = ZBCheck.collection
            await collection.update_one({'key': key}, {
                '$set': {
                    'organization': organization,
                    'meta_desc': meta_desc,
                    'for_check' : for_check,
                    'email_data' : email_data,
                    'response' : [{}],
                    'status': status
                }
            })
        else:
            raise AppErrors(f"NEVER HAPPENED: unknown parameter for renew={renew}")

        return need_credits


    async def _update_email_store(self,
                                  checked_emails):

        if checked_emails:
            collection = ZBEmail.collection
            try:
                return await collection.insert_many(checked_emails, ordered=False)
            except Exception as e:
                pass

        return None

    async def get_invalid(self,
                          emails,
                          valid_statuses):
        cursor = ZBEmail.find({'email' : {'$in' : emails}, 'status' : {'$nin' : valid_statuses}})

        objs = await cursor.to_list(length=10000)

        return [i.email for i in objs]
