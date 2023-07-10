import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.db.functions import *

async def coffee_start(message: types.Message, state: FSMContext):
    print(user_exists_in_db(message.from_id))
    if not user_exists_in_db(message.from_id):
        await message.answer('Вы ещё не заполняли анкету, сначала заполните анкету')
        await state.finish()
        return

    time = await get_time_next_match_from_db(message.from_id)
    print(time, type(time))

    if time > datetime.timedelta(0):
        await message.answer(f'Прошло недостаточно времени для получения нового контакта. Осталось {time}')
        await state.finish()
        return

    match_id = await get_user_id_coffee_from_db(message.from_id)
    print(match_id)
    if match_id == None:
        await message.answer('Мы не смогли найти анкету сейчас, попробуйте в другой раз или напишите в техподдержку')
        await state.finish()
        return

    user_id = message.from_id
    await add_match_to_db(user_id, match_id)

    await print_match_form(message, match_id)

def register_handlers_coffee(dp: Dispatcher):
    dp.register_message_handler(coffee_start, commands='coffee', state='*')

async def print_match_form(message, match_id):
    name = await get_name_from_db(match_id)
    photo = await get_photo_from_db(match_id)
    description = await get_description_from_db(match_id)
    user_id = message.from_id
    time = await get_time_next_match_from_db(user_id)
    try:
        await message.answer_photo(photo, f"Имя: {name}\nОписание: {description}\n"
                         f"Следующий контакт можно будет получить через {time}", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"Ошибка: {e}",
                                   reply_markup=types.ReplyKeyboardRemove())
