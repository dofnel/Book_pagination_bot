from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Id:
    ids: list[str]


@dataclass
class Config:
    tg_bot: TgBot
    id: Id


def load_config(path: str) -> Config:
    env: Env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN')),
                  id=Id(ids=env('ADMINS_ID')))
