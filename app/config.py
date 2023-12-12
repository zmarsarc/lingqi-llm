from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class AppSettings(BaseSettings):
    data_file_path: str = '/var/llm-main.db'
    session_file_path: str = '/var/llm-session.db'


app_settings = AppSettings()


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='auth_')
    expires: int = 3600
    verifiation_ttl: int = 900


auth_settings = AuthSettings()


class ChatSettings(BaseSettings):

    class BlacklistMode(str, Enum):
        Disable = 'disable'
        Block = 'block'
        Replace = 'replace'

    model_config = SettingsConfigDict(env_prefix='chat_')

    # API settings specify chat model API and connect timeout in seconds.
    api_url: str = 'http://www.lingqi.tech:8606/chat/chat'
    api_timeout: int = 15

    # For blacklist words filteration, mode can be 'disable', 'block' or 'replace'.
    # 'block' mode will block all content which include any words that in blacklist, and return block hint.
    # 'replace' mode will replace those words in content that in blacklist by its replacement word.
    # 'disable' mode do not check content, it just pass all content directly.
    #
    # A sample of blacklist conf:
    # [Hh]ello:some say hello...
    # [Pp]olice:GA
    #
    # each line represent a rule. before : can be a regexp, and after : is its replacement.
    blacklist_path: str = '/etc/llm/blacklist.conf'
    blacklist_mode: str = BlacklistMode.Block
    blacklist_block_hint: str = "请勿交流敏感信息"


chat_settings = ChatSettings()
