from logging import StreamHandler
import queue

from aiogram import Bot
from aiogram.types import User


class TelegramLoggerHandler(StreamHandler):
    def __init__(self, bot):
        StreamHandler.__init__(self)
        self.bot: Bot = bot
        self.user_id = None
        self.queue = queue.Queue(-1)

    def set_user(self, user: User):
        self.user_id = user.id

    def emit(self, record):
        self.queue.put(self.format(record))

    async def send_to_user(self):
        if not self.user_id:
            return
        while True:
            try:
                msg = self.queue.get(block=False)
                await self.bot.send_message(self.user_id, msg)
            except queue.Empty:
                break
