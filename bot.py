import asyncio
from config_data.config import load_config
from aiogram import Bot, Dispatcher
from handlers import user_handlers
from keyboards.main_menu import setup_menu_buttons


async def main():
    config = load_config('.env')
    API_TOKEN = config.tg_bot.token

    bot: Bot = Bot(API_TOKEN)
    dp: Dispatcher = Dispatcher()

    # Регистрация роутера
    dp.include_router(user_handlers.router)

    # Обновляет menu кнопки
    await setup_menu_buttons(bot)

    # Удаляем сообщения, которые пришли после предыдущего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
