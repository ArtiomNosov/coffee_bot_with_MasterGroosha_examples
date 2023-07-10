import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import load_config
from app.handlers.form import register_handlers_form
from app.handlers.edit import register_handlers_edit
from app.handlers.coffee import register_handlers_coffee
from app.handlers.faq import register_handlers_faq
from app.handlers.support import register_handlers_support
from app.handlers.common import register_hendlers_common

from app.db.functions import create_tables_if_not_exists

logger = logging.getLogger(__name__)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/form', description='Заполнить анкету'),
        BotCommand(command='/edit', description='Отредактировать анкету'),
        BotCommand(command='/coffee', description='Получить контакт'),
        BotCommand(command='/faq', description='Ответы на часто задаваемые вопросы'),
        BotCommand(command='/support', description='Техническая поддрежка'),
    ]
    await bot.set_my_commands(commands)

async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error('Starting bot')

    # Парсинг файла конфигурации
    config = load_config('config/bot.ini')

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_hendlers_common(dp, config.tg_bot.admin_id)
    register_handlers_form(dp)
    register_handlers_edit(dp)
    register_handlers_coffee(dp)
    register_handlers_faq(dp)
    register_handlers_support(dp)

    # Установка команд бота
    await set_commands(bot)
    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()

if __name__ == '__main__':
    create_tables_if_not_exists()
    asyncio.run(main())