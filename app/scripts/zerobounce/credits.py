from app.core.config import settings
from app.core.exceptions import *
from app.scripts.zerobounce.provider import _execute_zerobounce_api

async def zb_credits():
    settings.LOGGER.info("...showing credits")

    credits = await  _execute_zerobounce_api("get_credits")
    if not credits:
        settings.LOGGER.error(f"There is no credits created yet")

    settings.LOGGER.info(credits)

    return credits

async def zb_check_credits(need_credits):
    need_credits = int(need_credits)

    credits = await zb_credits()
    if not credits:
        raise AppErrors(f"Can't return empty result: zerobounce_credits res={credits}")

    count = int(credits['Credits'])

    if need_credits > count:
        settings.LOGGER.info(f"NOT ENOUGH CREDITS: you have={count} you need={need_credits} diff={need_credits-count}")
    else:
        settings.LOGGER.info(f"CREDITS ENOUGH: you have={count} you need={need_credits}")

    return count