import gspread
from app.core.config import settings
from app.core.exceptions import *
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
from typing import Any
import re
import gspread_formatting as gsf

class GspreadProvider():
    def __init__(self, direct=True):
        if direct:
            raise AppErrors("Must use async create_api_provider to create instance")

    @classmethod
    async def create_api_provider(cls,
                                  settings: dict=settings) -> Any:

        api_provider = cls(direct=False)

        api_provider.settings = settings
        api_provider.service = gspread.service_account_from_dict(info=settings.PUB_SUB_KEY)

        return api_provider

    async def worksheets(self):
        if not self.spreadsheet:
            raise AppErrors(f"NO SHEET: call open first")

        return self.spreadsheet.worksheets()

    async def create(self, customer):
        self.spreadsheet = self.service.create(f"{customer}-outreach-stats")

        print(f"SPREADSHEET CREATED for {customer}  url={self.spreadsheet.url}")
        self.spreadsheet.share('ks.shilov@gmail.com', perm_type='user', role='writer')

    async def open(self, url):
        self.spreadsheet = self.service.open_by_url(url)
        print(f"SPREADSHEET OPENED  url={self.spreadsheet.url}")

        return self.spreadsheet

    async def load_rows(self,
                        sheet,
                        start_row):
        if start_row <= 0:
            raise AppErrors("start_row MUST starts from 1")

        df = get_as_dataframe(sheet,
                              skiprows=range(0, start_row - 1),
                              evaluate_formulas=True,
                              skip_blank_lines=True)
        #remove empty rows
        df.dropna(axis=0, how='all', inplace=True)

        #remove empty columns
        df.dropna(axis=1, how='all', inplace=True)

        return df

    async def load_column(self, sheet, column, start_row):
        df = get_as_dataframe(sheet,
                                header=None,
                                na_filter=True,
                                usecols=[column],
                                skiprows=range(0,start_row),
                                skip_blank_lines=True)

        df.dropna(axis=0, inplace=True)

        return df

    async def update(self,
               sheet_title,
               data):
        if not self.spreadsheet:
            raise Exception("Call open/create spreadsheet first")

        sheet = self._create_or_clear(sheet_title)

        if isinstance(data, list):
            count = 1
            for d in data:
                set_with_dataframe(sheet,
                                   d,
                                   row=count,
                                   include_index=True)
                count = count + len(d.index) + 3
        else:
            set_with_dataframe(sheet,
                               data,
                               include_index=True)

        print(f"{sheet_title} updated")

    async def update_stats(self,
                           sheet,
                           stats):
        values = []
        for title, val in stats.items():
            values.append([title, val])

        return sheet.append_rows(values)

    async def mark_invalid_cells(self,
                                 sheet,
                                 cells,
                                 invalid_emails):
        invalid = gsf.cellFormat(
            backgroundColor=gsf.color(1, 0, 0)
        )
        catch_all = gsf.cellFormat(
            backgroundColor=gsf.color(1, 1, 0)
        )
        spamtrap = gsf.cellFormat(
            backgroundColor=gsf.color(0.5,0,0.5)
        )

        batch = gsf.batch_updater(sheet.spreadsheet)
        for cell in cells:
            email = cell.value
            status = invalid_emails[email]
            if status == 'invalid':
                batch.format_cell_range(sheet, cell.address, invalid)
            elif status == 'catch-all':
                batch.format_cell_range(sheet, cell.address, catch_all)
            elif status == 'spamtrap':
                batch.format_cell_range(sheet, cell.address, spamtrap)
            else:
                batch.format_cell_range(sheet, cell.address, invalid)

        return batch.execute()

    async def find_invalid_cells(self,
                                 sheet,
                                 emails_dict):

        query = self._create_regex(list(emails_dict.keys()))
        return sheet.findall(query)

    def _create_regex(self, emails):
        return re.compile("|".join(emails))

    def _create_or_clear(self,
                         sheet_title):

        sheet = None

        try:
            sheet = self.spreadsheet.worksheet(sheet_title)
            if sheet:
                sheet.clear()
        except Exception as e:
            print(str(e))
            sheet = self.spreadsheet.add_worksheet(title=sheet_title, rows="1000", cols="100")

        return sheet
