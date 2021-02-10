from .utils import *
from app.controllers.leads.downloader import LeadsDownloader
from app.controllers.leads.uploader import LeadsUploader
from app.controllers.closecom_custom_fields.controller import CloseComCustomFieldsController

async def upload_leads(customer):
    customer_config = load_customer_config(customer)
    if not customer_config:
        raise AppErrors(f"NOT FOUND: config for customer={customer} can't be loaded")

    system_fields = list_of_splitted_system_fields()

    controller = await LeadsUploader.create_controller(customer_config=customer_config)

    stats_new = await controller.upload_new(system_fields=system_fields)
    print("new leads uploaded")
    pprint(stats_new)

    stats_update = await controller.upload_updated(system_fields=system_fields)
    print("updated leads uploaded")
    pprint(stats_update)


async def create_leads(customer):
    stats = await _download_leads(customer, update=False)
    pprint(stats)

    return

async def update_leads(customer):
    stats = await _download_leads(customer, update=True)

    pprint(stats)

    return

async def _download_leads(customer, update):
    customer_config = load_customer_config(customer)
    if not customer_config:
        raise AppErrors(f"NOT FOUND: config for customer={customer} can't be loaded")

    controller = await LeadsDownloader.create_controller(customer_config=customer_config,
                                                         update=update)

    process_sheets = []

    fields_mapping = {}
    use_current = str(input("Use saved config? (Y/n)") or 'y').lower()

    if use_current == 'y':
        fields_mapping = customer_config['fields_mapping'].copy()
        try:
            new_fields_mapping = fields_mapping.copy()
            for sheet_id, data in fields_mapping.items():
                skip = str(input(f"Skip sheet={data['sheet_title']}? (N/y)") or "n").lower()
                if skip == 'y':
                    del new_fields_mapping[sheet_id]
                else:
                    process_sheets.append(data['sheet_title'])

            fields_mapping = new_fields_mapping.copy()
        except:
            pass
    else:
        work_sheets = await controller.download_sheets()
        if not work_sheets:
            raise AppErrors(f"DWONLOAD SHEETS not found = {work_sheets}")

        for sheet in work_sheets:
            try:
                skip = str(input(f"Skip sheet={sheet.title}? (N/y)") or "n")
                if skip.lower() == "y":
                    print(f"SKIPPING sheet={sheet.title}")
                    continue
                else:
                    process_sheets.append(sheet.title)

                saved_mapping = customer_config.get('fields_mapping', {}).get(sheet.id, None)
                if saved_mapping:
                    print("Saved mapping found:")
                    pprint(saved_mapping)
                    use_saved = str(input(f"Use saved mapping for {sheet.title}? (Y/n)") or "y")
                    if use_saved.lower() == 'y':
                        fields_mapping[sheet.id] = saved_mapping.copy()
                        continue

                header_row = int(input(f"Which row count is a header?"))
                base_fields = {
                    'header_row' : header_row,
                    'sheet_title' : sheet.title,
                    'contact_fields' : {

                    },
                    'lead_fields' : {

                    }
                }

                fields_mapping[sheet.id] = base_fields.copy()
                while True:
                    map_from = str(input("Map from spreadsheet column (case insensitive):")).strip().lower()
                    map_to = str(input("Map to (case insensitive):")).strip().lower()

                    is_lead = str(input("Lead (l) or contact(c)? (l/c)")).lower()
                    if is_lead == 'l':
                        fields_mapping[sheet.id]['lead_fields'][map_from] = map_to
                    elif is_lead == 'c':
                        fields_mapping[sheet.id]['contact_fields'][map_from] = map_to

                    the_end = str(input("Continue? (Y/n)") or 'y').lower()
                    if the_end != 'y':
                        pprint(fields_mapping[sheet.id])
                        correct = str(input("Is that correct? (Y/n)") or 'y').lower()
                        if correct != 'y':
                            fields_mapping[sheet.id] = base_fields.copy()
                            continue
                        else:
                            break


            except Exception as e:
                print(f"ERROR: can't process sheet={sheet.title} error={str(e)}")
                continue

        save = str(input("Save fields mappings? (Y/n)") or 'y').lower()
        if save == 'y':
            customer_config['fields_mapping'] = fields_mapping.copy()
            update_customer_config(customer, customer_config)
            controller.reload_customer_config(customer_config)

    print("The next sheets will be proceed:")
    pprint(process_sheets)

    ok = str(input("Continue? (Y/n)") or 'y').lower()
    if ok != 'y':
        return None

    pprint(fields_mapping)

    print("Check missing custom fields")
    await _create_missing_custom_fields(customer, fields_mapping)

    return await controller.download_leads(fields_mapping=fields_mapping)

async def update_custom_fields(customer):
    customer_config = load_customer_config(customer)
    if not customer_config:
        raise AppErrors(f"NOT FOUND: config for customer={customer} can't be loaded")

    controller = await CloseComCustomFieldsController.create_controller(customer_config=customer_config)

    await controller.update_lead_custom_fields()
    await controller.update_contact_custom_fields()

    await controller.on_shutdown()


async def _create_missing_custom_fields(customer, fields_mapping):
    customer_config = load_customer_config(customer)
    if not customer_config:
        raise AppErrors(f"NOT FOUND: config for customer={customer} can't be loaded")

    system_fields = list_of_system_fields()

    custom_lead_fields = set()
    custom_contact_fields = set()

    for sheet_id, data in fields_mapping.items():
        custom_contact_fields.update(list(data.get('contact_fields', {}).values()))
        custom_lead_fields.update(list(data.get('lead_fields', {}).values()))


    controller = await CloseComCustomFieldsController.create_controller(customer_config=customer_config)

    #Need to update all before cal missing

    #TODO: uncomment in production
    await controller.update_lead_custom_fields()
    await controller.update_contact_custom_fields()

    await controller.create_missing_fields(system_fields=system_fields,
                                           custom_lead_fields=list(custom_lead_fields),
                                           custom_contact_fields=list(custom_contact_fields))
    await controller.on_shutdown()


async def create_missing_custom_fields(customer):
    customer_config = load_customer_config(customer)
    if not customer_config:
        raise AppErrors(f"NOT FOUND: config for customer={customer} can't be loaded")

    if not customer_config.get('fields_mapping'):
        raise AppErrors(f"NO FIELDS MAPPING: fields_mapping not found for {customer} check config")

    fields_mapping = customer_config['fields_mapping'].copy()

    return await _create_missing_custom_fields(customer, fields_mapping)