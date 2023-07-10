import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.handlers.form import max_name_length, max_description_length
from app.db.functions import user_exists_in_db, save_form_to_db, get_name_from_db, get_photo_from_db, get_description_from_db

class EditForm(StatesGroup):
    ask_edit_name = State()
    waiting_for_name = State()
    ask_edit_photo = State()
    waiting_for_photo = State()
    ask_edit_description = State()
    waiting_for_description = State()

async def form_start(message: types.Message, state: FSMContext):
    if not user_exists_in_db(message.from_id):
        await message.answer('Вы ещё не заполняли анкету, сначала заполните анкету')
        await state.finish()
    await message.answer('Если вы хотите изменить имя, то напишите: да.')
    await state.set_state(EditForm.ask_edit_name.state)

async def edit_name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        await message.answer('Напишите своё имя')
        await state.set_state(EditForm.waiting_for_name.state)
    else:
        await state.set_state(EditForm.ask_edit_photo.state)
        await message.answer('Если вы хотите изменить фото, то напишите: да.')

async def name_inputted(message: types.Message, state: FSMContext):
    if len(message.text) > max_name_length:
        await message.answer('Пожалуйста, напишите имя короче 255 символов')
        return
    await state.update_data(name=message.text)

    await state.set_state(EditForm.ask_edit_photo.state)
    await message.answer('Если вы хотите изменить фото, то напишите: да.')

async def edit_photo(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        await message.answer('Отправте новое фото')
        await state.set_state(EditForm.waiting_for_photo.state)
    else:
        await state.set_state(EditForm.ask_edit_description.state)
        await message.answer('Если вы хотите изменить своё описание, то напишите: да.')

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
                await os.mkdir("users_info")
            if not os.path.isdir(f"users_info/tg_id={message.from_id}"):
                await os.mkdir(f"users_info/tg_id={message.from_id}")
            if not os.path.isdir(f"users_info/tg_id={message.from_id}/photos"):
                await os.mkdir(f"users_info/tg_id={message.from_id}/photos")
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file.getvalue())
        except Exception as e:
            await message.reply(e)

        await state.update_data(photo=downloaded_file.getvalue())
        await state.update_data(photo_name=file_info.file_path)
        await state.update_data(photo_path=src)

        await state.set_state(EditForm.ask_edit_description.state)
        await message.answer('Если вы хотите изменить своё описание, то напишите: да.')
    else:
        await message.answer('Пожалуйста, отправте своё фото')
        return

async def edit_description(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        await message.answer('Отправте новое описание анкеты')
        await state.set_state(EditForm.waiting_for_description.state)
    else:
        user_data = await state.get_data()
        await print_form(message, user_data)
        await save_form_to_db(message.from_id, user_data.get('name'), user_data.get('photo_name'),
                              user_data.get('photo_path'), None)
        await state.finish()
async def description_received(message: types.Message, state: FSMContext):
    if len(message.text) > max_description_length:
        await message.answer('Пожалуйста, сделайте описание короче 1024 символов.')
        return
    await state.update_data(description=message.text)
    user_data = await state.get_data()
    await print_form(message, user_data)
    await save_form_to_db(message.from_id, user_data.get('name'), user_data.get('photo_name'), user_data.get('photo_path'), message.text)
    await state.finish()

def register_handlers_edit(dp: Dispatcher):
    dp.register_message_handler(form_start, commands='edit', state='*')
    dp.register_message_handler(edit_name, state=EditForm.ask_edit_name)
    dp.register_message_handler(name_inputted, state=EditForm.waiting_for_name)
    dp.register_message_handler(edit_photo, state=EditForm.ask_edit_photo)
    dp.register_message_handler(photo_received, state=EditForm.waiting_for_photo, content_types=['photo'])
    dp.register_message_handler(edit_description, state=EditForm.ask_edit_description)
    dp.register_message_handler(description_received, state=EditForm.waiting_for_description)

async def print_form(message: types.Message, user_data):
    name = user_data.get('name')
    photo = None # user_data.get('photo')
    description = user_data.get('description')
    user_id = message.from_id
    if name == None:
        name = await get_name_from_db(user_id)
    if photo == None:
        photo = await get_photo_from_db(user_id)
    if description == None:
        description = await get_description_from_db(user_id)
    try:
        await message.answer_photo(photo, f"Ваше имя: {name}\nВашеописание: {description}\n"
                         f"Попробуйте теперь Получить контакт: /coffee", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"Ошибка: {e}",
                                   reply_markup=types.ReplyKeyboardRemove())
