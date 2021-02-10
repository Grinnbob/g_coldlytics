from zerobouncesdk import zerobouncesdk
from app.core.config import settings

def zb_init(api_key):
    zerobouncesdk.initialize(api_key)


def zb_send_file(file_path,
              email_address_column=1,
              has_header_row=True,
              return_url=None):

    return zerobouncesdk.send_file(
              file_path=file_path,
              email_address_column=email_address_column,
              return_url=return_url,
              has_header_row=has_header_row)

def zb_file_status(file_id):
    return zerobouncesdk.file_status(file_id)

def zb_delete_file(file_id):
    return zerobouncesdk.delete_file(file_id)

def zb_get_file(file_id,
             save_path):
    return zerobouncesdk.get_file(file_id, save_path)


