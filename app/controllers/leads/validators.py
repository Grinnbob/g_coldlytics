import os
import json
import traceback
import time

from app.core.exceptions import *
from app.core.config import settings
from pprint import pprint
from validate_email import validate_email

class BasicEmailValidator():
    def __init__(self, invalid_list):
        self.invalid_list = invalid_list

    def is_valid(self, email):
        email = str(email).strip().lower()
        if not validate_email(email):
            return False

        if email in self.invalid_list:
            return False

        return True
