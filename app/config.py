from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    data_file_path: str = '/var/data.db'


app_settings = AppSettings()
