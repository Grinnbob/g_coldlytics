from pathlib import Path
import os
import json
from app.core.exceptions import *
from app.core.config import settings
from app.providers.google.gdrive_service_api import GDriveServiceApiProvider
from pprint import pprint
from .utils import *

client_config = {
    "name" : "",  #Если используем 1 close.com account и нужно группировать лиды/письма и т.д.
    "organization": "coldlytics_agency",
    "api_key" : "",
    "sdr" : [], # с кем шарить созданные smartviews и кого добавлять в организацию
    "shared_list" : [], #с кем шарить созданные файлы

    "client_folder_id": "", #если будет какой-то функционал для автоматического создания файла используем это
    "client_folder_url": "", #для удобства - генерится автоматически

    "leads_spreadsheet" : "", #чтобы использовать для загрузки лидов
    "stats_spreadsheet" : "", #чтобы использовать для обновления статистки

    "smartview_count" : 8, # сколько указывать ограничение при создании smartview
    "warmup" : [1,1,2,2,3,3,3,3,1,1,1,1,2,2,2,1,1,1,4,3], #сколько раз запускать рассылку для каждого smartview
    "blacklist" : {
        "emails" : [],
        "domains" : []
    },

    "emails" : {},  #какие емайлы используются для данного клиента, если в howtosend есть емайл не из этого списка то ЭКСЕПШЕН

    "outreach" : {  # ЗАДАЕТСЯ ВРУЧНУЮ - список гипотез НА СТАРТЕ, на его базе генрируем howtosend
#       "h1" : {
#           "segment" : title,
#           "sequence" : title,
#           "email" : email from
#        },
#       "h2" : {}
#       .....
    },

    "howtosend" : {  #генерируется автоматически может правится вручную - то как делать рассылку
#       "smartview_id" : {
#           "sequence_id" : <id>,
#           "sequence_title" : <title>,
#           "sender" : <email from>
#        }
    },

    "sequences": {  #генерируется автоматически (чтобы понимать)
#       seq_id : title
    },
    "smartviews" : { #генерируется автоматически
#       smartview_id : title
    },
    "valid_leads" : ["valid", "catch-all"],
}


# Create google drive folder with leads and stats
async def create_customer(name):
    return create_customer_config(name,
                                  client_config=client_config)

async def setup_customer(name):
    return await create_drive(name)

async def create_drive(name):
    config_data = load_customer_config(name)
    drive_settings = settings.GOOGLE_SERVICE_ACCOUNT_SETTINGS

    api_provider = await GDriveServiceApiProvider.create_api_provider()

    #Root folder
    root_folder = []
    root_folder.append(drive_settings.get("gdrive_root_folder_id"))

    #Create folder
    folder = await api_provider.create_folder(config_data['name'],
                                              parents=root_folder)

    print("Clients folder created res=")
    pprint(folder)

    #save info about the folder
    if folder:
        config_data["client_folder_id"] = folder['id']
        config_data["client_folder_url"] = f"https://drive.google.com/drive/u/0/folders/{folder['id']}"


    #Copy spreadsheet to folder
    stats_template_id = drive_settings.get("gdrive_stats_template_id")
    leads_template_id = drive_settings.get("gdrive_leads_template_id")

    #customer_folder
    customer_folder = []
    customer_folder.append(config_data["client_folder_id"])

    stats_copy = await api_provider.copy_file(file_id=stats_template_id,
                                              new_name=f"{name}-stats",
                                              parents=customer_folder)
    print("Stats template copied res=")
    pprint(stats_copy)

    if not stats_copy:
        raise AppErrors(f"Can't create stats copy for {name}")
    else:
        config_data["stats_spreadsheet"] = f"https://docs.google.com/spreadsheets/d/{stats_copy['id']}"



    leads_copy = await api_provider.copy_file(file_id=leads_template_id,
                                              new_name=f"{name}-leads",
                                              parents=customer_folder)
    print("Leads template copied res=")
    pprint(leads_copy)

    if not leads_copy:
        raise AppErrors(f"Can't create leads copy for {name}")
    else:
        config_data["leads_spreadsheet"] = f"https://docs.google.com/spreadsheets/d/{leads_copy['id']}"

    update_customer_config(name,
                           config_data)

async def delete_drive(name):
    config_data = load_customer_config(name)

    api_provider = await GDriveServiceApiProvider.create_api_provider()

    res = await api_provider.delete_folder(config_data['name'])

    print(f"{name} delete success res:")
    pprint(res)


