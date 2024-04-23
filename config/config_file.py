from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBConfigs(BaseSettings):
    mongo_db_docker_host: str
    mongo_db_local_host: str
    mongo_db_docker_port: int
    mongo_db_local_port: int
    database: str
    mongo_username: str
    mongo_password: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class RedisDBConfigs(BaseSettings):
    redis_main_bot_docker_host: str
    redis_main_bot_docker_port: str
    redis_main_bot_local_host: str
    redis_main_bot_local_port: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class DatabaseConfigs(BaseSettings):
    mongo_db: MongoDBConfigs = Field(default_factory=MongoDBConfigs)
    redis_db: RedisDBConfigs = Field(default_factory=RedisDBConfigs)
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class DockerConfigs(BaseSettings):
    docker_telegram_server: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class RemoteServer(BaseSettings):
    remote_server_host: str
    remote_server_user_name: str
    remote_server_password: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class FileFormats(BaseSettings):
    video_formats: str
    audio_formats: str
    txt_format: str
    pdf_format: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class ChatGptConfigs(BaseSettings):
    gpt_model_version: str
    context_length: str
    gpt_model_temperature: float
    max_return_tokens: int
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class WhisperConfigs(BaseSettings):
    whisper_model_version: str
    whisper_language: str
    whisper_model_temperature: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class OpenAiConfigs(BaseSettings):
    openai_api_key: str
    chat_gpt: ChatGptConfigs = Field(default_factory=ChatGptConfigs)
    whisper: WhisperConfigs = Field(default_factory=WhisperConfigs)
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class PaymentConfigs(BaseSettings):
    yookassa_secret_key: str
    shop_id: str
    payments_provider_token_test: str
    payments_provider_token: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class LoggingConfig(BaseSettings):
    loger_bot_token: str
    LOGTAIL_INSIGTER_SOURCE: str
    telegram_chat_ids: str
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


class ProjectSettings(BaseSettings):
    telegram_bot_token: str
    test_telegram_bot_token: str
    docker_telegram_server: str
    progress_bar_server_url: str
    system: str
    server_download_path: str
    mixpanel: str
    open_ai: OpenAiConfigs = Field(default_factory=OpenAiConfigs)
    payment_configs: PaymentConfigs = Field(default_factory=PaymentConfigs)
    docker: DockerConfigs = Field(default_factory=DockerConfigs)
    data_base: DatabaseConfigs = Field(default_factory=DatabaseConfigs)
    remote_server: RemoteServer = Field(default_factory=RemoteServer)
    allowed_file_formats: FileFormats = Field(default_factory=FileFormats)
    logger_config:LoggingConfig = Field(default_factory=LoggingConfig)
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")



