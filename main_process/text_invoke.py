import asyncio
import os
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from os import path

import aiofiles
import chardet

from PyPDF2 import PdfReader

from costume_exceptions.file_read_exceptions import UnknownPDFreadFileError
from costume_exceptions.format_exceptions import EncodingDetectionError
from logging_module.log_config import insighter_logger
from settings import project_settings


from main_process.file_format_manager import FileFormatDefiner
from main_process.Whisper.whisper_dispatcher import MediaRecognitionFactory


class TextInvoker(ABC):
    @abstractmethod
    async def invoke_text(self, file_path):
        pass


class ITextInvokeFactory(ABC):
    @abstractmethod
    async def invoke_text(self, file_path):
        pass


class IPdfFileHandler(TextInvoker):
    async def invoke_text(self, file_path):
        raise NotImplementedError("Method invoke_text() must be implemented asynchronously")


class ITxtFileHandler(TextInvoker):
    async def invoke_text(self, file_path):
        raise NotImplementedError("Method invoke_text() must be implemented asynchronously")


class IVideoFileHandler(TextInvoker):
    async def invoke_text(self, file_path):
        raise NotImplementedError("Method invoke_text() must be implemented asynchronously")


class IAudioFileHandler(TextInvoker):
    async def invoke_text(self, file_path):
        raise NotImplementedError("Method transcribe_file() must be implemented asynchronously")


class PdfFileHandler(IPdfFileHandler):
    @staticmethod
    def get_text(file_path):
        with open(file_path, "rb") as file:
            try:
                pdf = PdfReader(file)
                content_pieces = [page.extract_text() if page.extract_text() else "" for page in pdf.pages]
                content = "".join(content_pieces)
                return content
            except UnknownPDFreadFileError as e:
                insighter_logger.exception("Something went wrong during invoking text from PDF in corutine function")
                raise UnknownPDFreadFileError from e

    async def invoke_text(self, file_path):
        file_path = path.normpath(file_path)
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
            try:
                result = await loop.run_in_executor(pool, self.get_text, file_path)
                return result
            except UnknownPDFreadFileError:
                insighter_logger.exception("Something went wrong during invoking text from PDF in invoke function")
            except Exception as e:
                insighter_logger.exception(f"Unknown Error named: {e}")


class TxtFileHandler(ITxtFileHandler):
    async def invoke_text(self, file_path):
        task = asyncio.create_task(self.__detect_encoding_fast(file_path))
        try:
            encoding = await task
            async with aiofiles.open(file_path, "r", encoding=encoding) as t:
                content = await t.read()
            return content
        except EncodingDetectionError:
            insighter_logger.exception("Unknown encoding detection error")

    @staticmethod
    async def __detect_encoding_fast(file_path, sample_size=1024):
        async with aiofiles.open(file_path, "rb") as f:
            sample = await f.read(sample_size)
        try:
            result = chardet.detect(sample)
            encoding = result["encoding"]
            insighter_logger.info("Successful encoding detection: %s", encoding)
            return encoding
        except Exception as e:  # На практике следует уточнить тип исключения
            insighter_logger.exception("Unknown encoding detection error: %s", e)
            raise EncodingDetectionError(f"Unknown encoding detection error: {e}") from e


class VideoFileHandler(IVideoFileHandler):
    def __init__(self, ai_transcriber: MediaRecognitionFactory):
        self.__recognizer = ai_transcriber

    async def invoke_text(self, file_path):
        try:
            result = await self.__recognizer.compile_transcription(file_path=file_path)
            insighter_logger.info("Text from VIDEO successfully invoked.")
            return result
        except Exception as e:
            insighter_logger.exception(f"something went wrong in text from Video invoking process. Error: {e}")


class AudioFileHandler(IAudioFileHandler):
    def __init__(self, ai_transcriber: MediaRecognitionFactory):
        self.__recognizer = ai_transcriber

    async def invoke_text(self, file_path):
        try:
            result = await self.__recognizer.compile_transcription(file_path=file_path)
            insighter_logger.info("Text from AUDIO successfully invoked.")
            return result
        except Exception as e:
            insighter_logger.exception(f"something went wrong in text from Video invoking process. Error: {e}")


@dataclass
class FORMATS:
    VIDEO_FORMATS: list[str]
    AUDIO_FORMATS: list[str]

    def __init__(self):
        self.__load_formats_from_env()

    def __load_formats_from_env(self) -> None:

        self.VIDEO_FORMATS = project_settings.allowed_file_formats.video_formats
        self.AUDIO_FORMATS = project_settings.allowed_file_formats.audio_formats
        if isinstance(project_settings.allowed_file_formats.video_formats, str):  # Проверка формата строки
            self.VIDEO_FORMATS = project_settings.allowed_file_formats.video_formats.split(",")
        if isinstance(project_settings.allowed_file_formats.audio_formats, str):
            self.AUDIO_FORMATS = project_settings.allowed_file_formats.audio_formats.split(",")

    def make_list_of_formats(self) -> list[str]:  # Указываем возвращаемый тип
        all_formats = self.VIDEO_FORMATS + self.AUDIO_FORMATS
        return all_formats


class TextInvokeFactory(ITextInvokeFactory):
    def __init__(
            self,
            format_definer: FileFormatDefiner,
            pdf_handler: IPdfFileHandler,
            txt_handler: ITxtFileHandler,
            video_handler: IVideoFileHandler,
            audio_handler: IAudioFileHandler,
            formats: FORMATS,
    ):
        self._format_definer = format_definer
        self._video_handler = video_handler
        self._audio_handler = audio_handler
        self._txt_handler = txt_handler
        self._pdf_handler = pdf_handler
        self.formats = formats

    async def invoke_text(self, file_path: str) -> str:
        try:
            invoker = await self.__create_invoker(file_path)
        except EncodingDetectionError as e:
            insighter_logger.exception(e, "Failf to invoke text")
            raise EncodingDetectionError from e

        try:
            text = await invoker.invoke_text(file_path)
            insighter_logger.info("text invoked")
            return text
        except Exception as e:
            insighter_logger.exception(e, "Failf to invoke text")
            raise e

    async def __create_invoker(self, file_path):
        income_file_format = await self._format_definer.define_format(file_path=file_path)
        if income_file_format in self.formats.VIDEO_FORMATS:
            return self._video_handler
        elif income_file_format in self.formats.AUDIO_FORMATS:
            return self._audio_handler
        else:
            # TODO логировать все новые файлы
            insighter_logger.exception(f"This file format {income_file_format} havent supported")
            raise EncodingDetectionError(f"This file format {income_file_format} havent supported")
        # TODO Выдать что формат не правильный вывести в сообщение бот ( точно правильное место )
