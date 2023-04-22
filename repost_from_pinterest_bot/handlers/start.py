from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Text

from keyboards import make_config_keyboard
from posting_manager import PostingManager
from telegram_logger import TelegramLoggerHandler

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext, telegram_logger_handler: TelegramLoggerHandler,
                    posting_manager: PostingManager):
    telegram_logger_handler.set_user(message.from_user)
    text = posting_manager.human_readable_settings() + "\nДля конфигурации воспользуйтесь коммандой /configure"
    await state.clear()
    await message.answer(text=text, reply_markup=make_config_keyboard())


@router.message(Text("Повторить"))
async def reset(message: Message, state: FSMContext, posting_manager: PostingManager):
    await state.clear()
    if posting_manager.settings:
        await posting_manager.change_settings(posting_manager.settings)
        await message.answer(text="Загружаем картинки заново", reply_markup=make_config_keyboard())
    else:
        await message.answer(text="Бот не настроен, нечего повторять", reply_markup=make_config_keyboard())


@router.message(Text("Сброс"))
async def reset(message: Message, state: FSMContext, posting_manager: PostingManager):
    await state.clear()
    await posting_manager.change_settings(None)
    await message.answer(text="Настройки сброшены, постинг остановлен", reply_markup=make_config_keyboard())
