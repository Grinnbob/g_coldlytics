from pathlib import Path
import os
import json
from app.core.exceptions import *
from app.core.config import settings
from pprint import pprint

CONFIG_FOLDER_TEMPLATE = "configs/{name}"
CONFIG_FILE_TEMPLATE = "{name}_config.json"

SHEET_COLS = {
    'a' : 0,
    'b' : 1,
    'c' : 2,
    'd' : 3,
    'e' : 4,
    'f' : 5,
    'g' : 6,
    'h' : 7,
    'i' : 8,
    'j' : 9,
    'k' : 10,
    'l' : 11,
    'm' : 12,
    'n' : 13,
    'o' : 14,
    'p' : 15,
    'q' : 16,
    'r' : 17,
    's' : 18,
    't' : 19,
    'u' : 20,
    'v' : 21,
    'w' : 22,
    'x' : 23,
    'y' : 24,
    'z' : 25,
}

def _path_config(name):
    path = Path(__file__).parent / CONFIG_FOLDER_TEMPLATE.format(name=name)
    config_file = path / CONFIG_FILE_TEMPLATE.format(name=name)

    return path, config_file

def create_customer_config(name, client_config):
    path, config_file = _path_config(name)

    try:
        path.mkdir(parents=True, exist_ok=False)
        config_file.touch(exist_ok=False)

        client_config["name"] = name
        with open(config_file, 'w') as output:
            json.dump(client_config, output, indent=4)

    except FileExistsError:
        print(f"{name} customer exist")
    else:
        print(f"{name} customer created")
        print(f"path: {config_file}")


def update_customer_config(name, data):
    path, config_file = _path_config(name)

    with open(config_file, 'w') as output:
        json.dump(data, output, indent=4)


def load_customer_config(name):
    path, config_file = _path_config(name)

    data = {}
    try:
        with config_file.open() as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"{name} client NOT created yet call: --create-client <name>")

    if not data:
        raise AppErrors(f"Bad config for {name}")

    name = data['name']
    if not name:
        raise AppErrors(f"config name={name} parameter can't be empty")

    return data

def create_chek_key(spreadsheet_id,
                    sheet_id):
    return str(spreadsheet_id) + '_' + str(sheet_id)

def get_sheet_id_from_key(key):
    return key.split('_')[-1]

def list_of_splitted_system_fields():
    return {
        'lead' : [
            'name',
            'display_name',
            'url',
            'description',
            'status_label',
            'primary_address'
        ],
        'contact' : [
            'name',
            'first_name',
            'last_name',
            'title',
            'email',
            'primary_phone',
            'primary_email',
            'primary_url'
        ]
    }

def list_of_system_fields():
    return [
        'name',
        'email',
        'display_name',
        'title',
        'first_name',
        'last_name',
        'primary_phone',
        'primary_email',
        'primary_url',
        'url',
        'description',
        'status_label',
        'primary_address',
    ]
