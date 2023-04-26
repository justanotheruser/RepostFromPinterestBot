from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from bot_settings import BotSettings
from keyboards import make_row_keyboard
from posting_manager import PostingManager
from telegram_logger import TelegramLoggerHandler

router = Router()

available_image_number_choices = [str(i) for i in (5, 10, 20, 50, 100)]
available_posting_frequencies = [str(i) for i in (1, 2, 3, 5, 8)]  # in hours


class ConfigurePosting(StatesGroup):
    choosing_queries = State()
    choosing_number_of_images = State()
    choosing_frequency = State()


@router.message(Command("configure"))
async def cmd_start(message: Message, telegram_logger_handler: TelegramLoggerHandler, state: FSMContext):
    telegram_logger_handler.set_user(message.from_user)
    await state.set_state(ConfigurePosting.choosing_queries)
    await message.answer(text="Введите список ключей")


@router.message(ConfigurePosting.choosing_queries)
async def queries_chosen(message: Message, state: FSMContext):
    await state.update_data(queries=message.text.lower().splitlines())
    await state.set_state(ConfigurePosting.choosing_number_of_images)
    await message.answer(text="Выберите кол-во картинок для парсинга",
                         reply_markup=make_row_keyboard(available_image_number_choices))


@router.message(ConfigurePosting.choosing_number_of_images, F.text.in_(available_image_number_choices))
async def number_of_images_chosen(message: Message, state: FSMContext):
    await state.update_data(number_of_images=int(message.text.lower()))
    await state.set_state(ConfigurePosting.choosing_frequency)
    await message.answer(text="Выберите, как часто надо постить",
                         reply_markup=make_row_keyboard(available_posting_frequencies))


@router.message(ConfigurePosting.choosing_frequency, F.text.in_(available_posting_frequencies))
async def posting_frequency_chosen(message: Message, state: FSMContext, posting_manager: PostingManager):
    await state.update_data(posting_frequency=int(message.text.lower()))
    user_data = await state.get_data()
    bot_settings = BotSettings(
        pinterest=BotSettings.Pinterest(queries=user_data['queries'], number_of_images=user_data['number_of_images']),
        posting=BotSettings.Posting(frequency_hours=user_data['posting_frequency']))
    await message.answer(
        text=f"Вы выбрали парсить по {bot_settings.pinterest.number_of_images} картинок, найденных по ключам "
             f"{bot_settings.pinterest.queries} и постить их раз в {bot_settings.posting.frequency_hours} час(а/ов)",
        reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await posting_manager.change_settings(bot_settings)
