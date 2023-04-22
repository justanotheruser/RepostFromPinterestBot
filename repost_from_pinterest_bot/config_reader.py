import os

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    bot_settings_file: str
    images_root_dir: str
    channel_id: str
    bot_admin_user_id: int

    class Config:
        env_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')
        env_file_encoding = 'utf-8'


config = Settings()
