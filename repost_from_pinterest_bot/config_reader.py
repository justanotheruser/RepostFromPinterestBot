from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    bot_settings_file: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
