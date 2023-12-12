from pydantic_settings import BaseSettings, SettingsConfigDict


class MsgSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='msg_')

    smtp_host: str = 'smtp.exmail.qq.com'


msg_settings = MsgSettings()


class MsgSecrets(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/run/secrets')

    smtp_username: str
    smtp_password: str


msg_secrets = MsgSecrets()
