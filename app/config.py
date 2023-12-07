from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    data_file_path: str = '/var/llm-main.db'
    session_file_path: str = '/var/llm-session.db'


app_settings = AppSettings()


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')

    expires: int = 3600


auth_settings = AuthSettings()
