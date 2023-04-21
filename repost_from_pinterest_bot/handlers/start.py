from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from repost_from_pinterest_bot.telegram_logger import TelegramLoggerHandler

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext, telegram_logger_handler: TelegramLoggerHandler):
    telegram_logger_handler.set_user(message.from_user)
    await state.clear()
    await message.answer(text="Для конфигурации воспользуйтесь коммандой /configure",
        reply_markup=ReplyKeyboardRemove())
