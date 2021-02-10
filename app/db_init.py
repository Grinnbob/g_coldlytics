from app.services import instance
import asyncio
from app.core.database import get_db

from app.services.zerobounce.models import *
from app.services.closecom.models import *
from bson.objectid import ObjectId

db = get_db()
instance.init(db)

async def _ensure_index():
    await ZBCheck.ensure_indexes()
    await ZBEmail.ensure_indexes()
    await CloseComCustomField.ensure_indexes()
    await CloseComLead.ensure_indexes()


async def main(loop):
    await _ensure_index()

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()