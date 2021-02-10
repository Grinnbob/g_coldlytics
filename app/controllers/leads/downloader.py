from app.core.exceptions import *
from app.controllers.leads.validators import BasicEmailValidator

from app.providers.google.gspread_api import GspreadProvider

from app.services.zerobounce.service import ZeroBounceService
from app.services.closecom.service import CloseComService
import traceback
from .closecom_serializer import CloseComLeadSerializer
from .stats import SpreadSheetStats

class LeadsDownloader():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_controller to create instance")

        self.gspread_provider = None
        self.stats = SpreadSheetStats()

    @classmethod
    async def create_controller(cls,
                                customer_config,
                                update=False):
        controller = cls(direct=False)

        controller.customer_config = customer_config.copy()
        controller.customer_name = customer_config.get('name', 'unknown_customer')

        controller.update = update
        controller.internal_status = 'create'
        if update:
            controller.internal_status = 'update'

        return controller

    def reload_customer_config(self, new_data):
        self.customer_config = new_data.copy()

    async def download_leads(self, fields_mapping):
        work_sheets = await self.download_sheets()

        closecom_service = CloseComService()


        self.stats.reset_stats()

        ids = list(fields_mapping.keys())
        for sheet in work_sheets:
            if str(sheet.id) not in ids:
                continue

            try:
                leads = await self._process_sheet(sheet=sheet,
                                                  mapping=fields_mapping[str(sheet.id)])
                if leads:
                    self.stats.set_stats_metric(sheet=sheet,
                                                metric='leads_found',
                                                value=len(leads.keys()))

                    total = await closecom_service.save_from_spreadsheet(leads=leads,
                                                                         update=self.update)
                    if total <= 0:
                        #print(f"ERROR save_from_spreadsheet for sheet={sheet.title}")
                        self.stats.set_stats_metric(sheet=sheet,
                                                    metric='skipped',
                                                    value=len(leads.keys()))
                    else:
                        if self.update:
                            self.stats.set_stats_metric(sheet=sheet,
                                                        metric='leads_updated',
                                                        value=total)
                        else:
                            self.stats.set_stats_metric(sheet=sheet,
                                                        metric='leads_created',
                                                        value=total)


                else:
                    print(f"NOT FOUND: leads not found for sheet={sheet.title}")
            except Exception as e:
                traceback.print_exc()
                print(f"ERROR: can't process sheet={sheet.title} error={str(e)}")
                continue

        return self.stats.raw_stats()

    async def download_sheets(self):
        leads_url = self.customer_config['leads_spreadsheet']
        if not leads_url:
            raise AppErrors(f"EMPTY URL: lead spreadsheet url empty url={leads_url}")

        gspread_provider = await self._gspread_provider()
        spreadsheet = await gspread_provider.open(leads_url)
        if not spreadsheet:
            raise AppErrors(f"OPEN ERROR: can't open spreadsheet={leads_url}  res={spreadsheet}")

        work_sheets = await gspread_provider.worksheets()
        if not work_sheets:
            raise AppErrors(f"NO WORKSHEETS: no worksheets found for spreadsheet={leads_url}")

        return work_sheets

    async def _process_sheet(self,
                             sheet,
                             mapping):

        header_row = mapping['header_row']

        contact_fields = mapping['contact_fields']
        inv_contact_fields = {v: k for k, v in contact_fields.items()}

        lead_fields = mapping['lead_fields']
        inv_lead_fields = {v: k for k, v in lead_fields.items()}
        lead_name_title = inv_lead_fields.get('name', None)
        if not lead_name_title:
            raise AppErrors(f"ERROR LEAD NAME: field not found for sheet={sheet.title}")


        email_column_title = inv_contact_fields.get('email', None)
        if not email_column_title:
            raise AppErrors(f"ERROR EMAIL: field not found for sheet={sheet.title}")

        gspread_provider = await self._gspread_provider()
        df = await gspread_provider.load_rows(sheet=sheet,
                                              start_row=header_row)

        df = await self._remove_invalid_emails(sheet=sheet,
                                               df=df,
                                               email_column_title=email_column_title)

        return await self._create_leads(df=df,
                                        mapping=mapping)

    async def _create_leads(self,
                            df,
                            mapping):

        serializer = CloseComLeadSerializer(organization=self.customer_name,
                                            internal_status=self.internal_status)

        return serializer.serialize_leads_array(df=df,
                                                mapping=mapping)

    async def _remove_invalid_emails(self,
                                     sheet,
                                     df,
                                     email_column_title):

        df.rename(columns=lambda x: x.strip().lower(), inplace=True)
        email_column_title = email_column_title.strip().lower()
        emails = df[email_column_title].dropna().tolist()

        self.stats.set_stats_metric(sheet=sheet,
                                    metric='total_contacts',
                                    value=len(emails))

        zb_service = ZeroBounceService()
        valid_statuses = self.customer_config.get('valid_leads', None)
        if not valid_statuses:
            valid_statuses = ['valid']

        invalid_emails = await zb_service.get_invalid(emails, valid_statuses)

        validator = BasicEmailValidator(invalid_emails)

        df = df[df[email_column_title].map(validator.is_valid) == True]

        self.stats.set_stats_metric(sheet=sheet,
                                    metric='valid_contacts',
                                    value=len(df.index))


        df.fillna('', inplace=True)

        return df

    async def _gspread_provider(self):
        if not self.gspread_provider:
            self.gspread_provider = await GspreadProvider.create_api_provider()

        return self.gspread_provider