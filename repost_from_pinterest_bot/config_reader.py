import os

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    bot_settings_file: str
    images_root_dir: str
    channel_id: str
    bot_admin_user_id: int
    failed_pages_dir: str

    class Config:
        env_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env')
        env_file_encoding = 'utf-8'


config = Settings()
config.bot_settings_file = os.path.expanduser(config.bot_settings_file)
config.images_root_dir = os.path.expanduser(config.images_root_dir)
config.failed_pages_dir = os.path.expanduser(config.failed_pages_dir)
