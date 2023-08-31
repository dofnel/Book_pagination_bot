from aiogram.types import BotCommand
from aiogram import Bot
from lexicon.lexicon import LEXICON_COMMANDS


async def setup_menu_buttons(bot: Bot):
    commands = [BotCommand(command=com,
                           description=des) for com, des in LEXICON_COMMANDS.items()]

    await bot.set_my_commands(commands)
