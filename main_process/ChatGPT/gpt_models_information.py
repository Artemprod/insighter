# Определение названий моделей GPT
import asyncio



from costume_exceptions.config_loading import (
    APIKeyLoadError,
    ContextLengthLoadingError,
    ModelTempretureLoadingError,
    ModelVersionLoadingError,
)
from settings import project_settings



# Словарь, содержащий информацию о максимальном числе токенов для каждой модели
GPTModelsInfo = {
    "gpt-3.5": 2048,
    "gpt-3.5-turbo-0613": 4097,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-4": 2048,
    "gpt-4-0314": 2048,
    "gpt-4-32k-0314": 32768,
    "gpt-4-0613": 2048,
    "gpt-4-32k-0613": 32768,
}


class GPTModelManager:
    def __init__(self):
        self.models_info = GPTModelsInfo

    async def get_current_gpt_model_max_size(self) -> int:
        """Возвращает максимальный размер токенов для текущей используемой модели GPT."""
        # Преобразование строки в enum, если это возможно. В противном случае будет выброшено исключение.
        current_model = await self.get_current_gpt_model_in_use_from_env()
        max_size = self.models_info.get(current_model)
        if max_size:
            return max_size
        else:
            raise ValueError(f"Model {current_model} not found")

    async def get_current_gpt_model_in_use_from_env(self) -> str:
        """
        Method loads actual length of conversation context
        :return:
        """

        try:
            return project_settings.open_ai.chat_gpt.gpt_model_version
        except Exception as e:
            insighter_logger.exception(f"Failed to load model version. Error {e} in class {self.__dict__}")
            raise ModelVersionLoadingError(f"Failed to load model version. Error {e} in class {self.__dict__}") from e

    async def get_current_context_length(self) -> int:
        """
        Method loads chat gpt model from config env file
        :return:
        """
        try:
            return project_settings.open_ai.chat_gpt.context_length
        except Exception as e:
            insighter_logger.exception(f"Failed to load model token capacity. "
                                       f"Error {e} in class {self.__dict__}")
            raise ContextLengthLoadingError(f"Failed to load model token capacity. "
                                            f"Error {e} in class {self.__dict__}") from e

    async def get_gpt_api_key(self):
        try:
            return project_settings.open_ai.openai_api_key
        except Exception as e:
            insighter_logger.exception(f"Failed to load open ai key. Error {e} in class {self.__dict__}")
            raise APIKeyLoadError(f"Failed to load open ai key. Error {e} in class {self.__dict__}") from e

    async def get_gpt_model_tempreture(self):
        try:
            return project_settings.open_ai.chat_gpt.gpt_model_temperature
        except Exception as e:
            insighter_logger.exception(
                f"Failed to load open ai temperature parameter. Error {e} in class {self.__dict__}"
            )
            raise ModelTempretureLoadingError(
                f"Failed to load open ai model temperature parameter. Error {e} in class {self.__dict__}"
            ) from e

    async def get_max_return_tokens(self):

        try:
            return project_settings.open_ai.chat_gpt.max_return_tokens
        except Exception as e:
            insighter_logger.exception(
                f"Failed to load open ai return tokens amount parameter. Error {e} in class {self.__dict__}"
            )
            raise ModelTempretureLoadingError(
                f"Failed to load open ai return tokens amount parameter. Error {e} in class {self.__dict__}"
            ) from e


async def main():
    a = GPTModelManager()
    insighter_logger.info(await a.get_current_gpt_model_max_size())


if __name__ == "__main__":
    asyncio.run(main())
