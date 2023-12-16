import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.db.functions import *

max_name_length = 255
max_description_length = 1024

class FillInTheForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_photo = State()
    waiting_for_description = State()

async def form_start(message: types.Message, state: FSMContext):
    if user_exists_in_db(message.from_id):
        await message.answer('Вы уже заполняли анкету! Чтобы отредактировать её используйьте команду /edit')
        await state.finish()
        return

    await message.answer('Напишите своё имя')
    await state.set_state(FillInTheForm.waiting_for_name.state)

async def name_inputted(message: types.Message, state: FSMContext):
    if len(message.text) > max_name_length:
        await message.answer('Пожалуйста, напишите имя короче 255 символов')
        return
    await state.update_data(name=message.text)

    await state.set_state(FillInTheForm.waiting_for_photo.state)
    await message.answer('Теперь пришлите своё фото')

async def photo_received(message: types.message, state: FSMContext):
    if message.photo:
        await message.answer('Ого это фото!')
        try:
            file_info = await message.bot.get_file(message.photo[-1].file_id)
            downloaded_file = await message.bot.download_file(file_info.file_path)
            src = f'users_info/tg_id={message.from_id}/{file_info.file_path}'
        except Exception as e:
            await message.reply(e)

        try:
            if not os.path.isdir("users_info"):
                os.mkdir("users_info")
            if not os.path.isdir(f"users_info/tg_id={message.from_id}"):
                os.mkdir(f"users_info/tg_id={message.from_id}")
            if not os.path.isdir(f"users_info/tg_id={message.from_id}/photos"):
                os.mkdir(f"users_info/tg_id={message.from_id}/photos")
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())
        except Exception as e:
            await message.reply(e)

        await state.update_data(photo=downloaded_file.getvalue())
        await state.update_data(photo_name=file_info.file_path)
        await state.update_data(photo_path=src)

        await state.set_state(FillInTheForm.waiting_for_description.state)
        await message.answer('Теперь пришли свои контакты с описанием')
    else:
        await message.answer('Пожалуйста, отправте своё фото')
        return


async def description_received(message: types.Message, state: FSMContext):
    if len(message.text) > max_description_length:
        await message.answer('Пожалуйста, сделайте описание короче 1024 символов.')
        return
    user_data = await state.get_data()
    await message.answer_photo(user_data.get('photo'), f"Вы {user_data.get('name')} и описанием {message.text}\n"
                         f"Попробуйте теперь Получить контакт: /coffee", reply_markup=types.ReplyKeyboardRemove())

    await save_form_to_db(message.from_id, user_data.get('name'), user_data.get('photo_name'), user_data.get('photo_path'), message.text)
    await state.finish()

def register_handlers_form(dp: Dispatcher):
    dp.register_message_handler(form_start, commands='form', state='*')
    dp.register_message_handler(name_inputted, state=FillInTheForm.waiting_for_name)
    dp.register_message_handler(photo_received, state=FillInTheForm.waiting_for_photo, content_types=['photo'])
    dp.register_message_handler(description_received, state=FillInTheForm.waiting_for_description)