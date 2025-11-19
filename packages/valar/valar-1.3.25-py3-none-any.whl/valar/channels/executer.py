import asyncio
import traceback

from ..channels.sender import ValarChannelSender
from django.db import close_old_connections


async def execute_channel(method, sender: ValarChannelSender):
    thread = asyncio.to_thread(__execute__, method, sender)
    asyncio.create_task(thread)


def __execute__(method, sender: ValarChannelSender):
    close_old_connections()

    sender.start()
    try:
        response = method(sender)
        sender.done(response)
        sender.stop()
    except Exception as e:
        traceback.print_exc()
        sender.error(str(e))
        sender.stop()
