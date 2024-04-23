from environs import Env

from costume_exceptions.config_loading import (
    APIKeyLoadError,
    ModelVersionLoadingError,
    WhisperLanguageLoadError,
)
from settings import project_settings
from logging_module.log_config import insighter_logger


class WhisperModelManager:
    def get_current_whisper_model_in_use_from_env(self) -> str:
        """
        Method loads actual whisper model fro api
        :return:
        """

        try:
            return project_settings.open_ai.whisper.whisper_model_version
        except Exception as e:
            insighter_logger.exception(f"Failed to load model version. Error {e} in class {self.__dict__}")
            raise ModelVersionLoadingError(f"Failed to load model version. Error {e} in class {self.__dict__}") from e

    def get_gpt_api_key(self):
        try:
            return project_settings.open_ai.openai_api_key
        except Exception as e:
            insighter_logger.exception(f"Failed to load open ai key. Error {e} in class {self.__dict__}")
            raise APIKeyLoadError(f"Failed to load open ai key. Error {e} in class {self.__dict__}") from e

    def get_whisper_language(self):
        try:
            return project_settings.open_ai.whisper.whisper_language
        except Exception as e:
            insighter_logger.exception(f"Failed to load language. Error {e} in class {self.__dict__}")
            raise WhisperLanguageLoadError(f"Failed to load language. Error {e} in class {self.__dict__}") from e

    def get_temperature(self):
        try:
            return project_settings.open_ai.whisper.whisper_model_temperature
        except Exception as e:
            insighter_logger.exception(f"Failed to load language. Error {e} in class {self.__dict__}")
            raise WhisperLanguageLoadError(f"Failed to load language. Error {e} in class {self.__dict__}") from e
