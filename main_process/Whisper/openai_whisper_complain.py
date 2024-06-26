import asyncio

import openai
from openai import AsyncOpenAI

from costume_exceptions.ai_exceptions import EmptyResponseArrayError
from logging_module.log_config import insighter_logger
from main_process.Whisper.whisper_information import WhisperModelManager


class WhisperClient:
    def __init__(self, whisper_manager: WhisperModelManager):
        self.__whisper_manager = whisper_manager
        self.__model_name = self.__whisper_manager.get_current_whisper_model_in_use_from_env()
        openai.api_key = self.__whisper_manager.get_gpt_api_key()
        self.client = AsyncOpenAI()
        # TODO придумать как классно можно обрабюотать доп рпомпты
        self.bad_word_prompt = "Эм..Ага, так, да,да..."
        self.punctuation_prompt = "Добрый день, спасибо что пришли! Сегодня..."

    async def __load_prompts(self):
        return (f"{self.punctuation_prompt}, {self.bad_word_prompt}",)

    # TODO передавть уже подговтоленые данные ( S3 хранение данных или буфер хранить на облочных хранилищах ) мно может и пофиг
    # Передовать байты сюда просто берет данные и передает реквести
    async def whisper_compile(self, file_path, prompts="", context=""):
        """Given a prompt, transcribe the audio file."""
        language = self.__whisper_manager.get_whisper_language()
        temperature = self.__whisper_manager.get_temperature()
        with open(file_path, mode="rb") as file_:
            gpt_args = {
                "model": self.__model_name,
                "prompt": prompts + context,
                "file": file_,
                "language": language,
                "temperature": temperature,
            }
            insighter_logger.info(f"gpt args: {gpt_args}")
            response = await self.__request(gpt_args)
            return response

    async def __request(self,
                        gpt_args: dict) -> str:
        task = self.client.audio.transcriptions.create(**gpt_args)
        if task is None:
            raise ValueError("Task is None!")
        response = await task
        if response.text:
            insighter_logger.info("response from whisper received")
            return response.text
        else:
            insighter_logger.exception("No data returned in the response.")
            raise EmptyResponseArrayError("No data returned in the response.")
