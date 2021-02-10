from app.core.exceptions import *
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from app.core.database import get_db
from . import instance
import traceback

class CLBaseService():
    def __init__(self):
        initialized = False
        try:
            exist = instance.db
            if exist:
                initialized = True
        except Exception as e:
            initialized = False
            self.db = None

        if not initialized:
            self.db = get_db()
            instance.init(self.db)