import asyncio

import aiofiles.tempfile

from costume_exceptions.ai_exceptions import (
    AsyncTranscribitionError,
    LoadingLongTranscriberError,
    LoadingShorthandsTranscriberError,
    MediaSizeError,
    ShortMediaTranscribitionError,
    TranscribitionError,
)
from logging_module.log_config import insighter_logger
from main_process.func_decorators import ameasure_time
from main_process.media_file_manager import MediaFileManager
from main_process.Whisper.openai_whisper_complain import WhisperClient


class MediaFileTranscriber:
    def __init__(self, whisper_client: WhisperClient):
        self.whisper_client = whisper_client

    async def transcribe_media(self, file) -> str:
        raise NotImplementedError


# noinspection PyTypeChecker
class ShortMediaFilesTranscriber(MediaFileTranscriber):
    async def transcribe_media(self, file) -> str:

        task = asyncio.create_task(self.whisper_client.whisper_compile(file_path=file))
        try:
            recognized_text = await task
            insighter_logger.info("Successfully transcribe file")
            return recognized_text
        except Exception as e:
            insighter_logger.exception(f"Failed to transcribe short media file. exception {e}")
            raise ShortMediaTranscribitionError(exception=e) from e


class LongMediaFilesTranscriber(MediaFileTranscriber):
    def __init__(
            self,
            whisper_client: WhisperClient,
            media_file_manager: MediaFileManager,
    ):
        super().__init__(whisper_client)
        self.__media_file_manager = media_file_manager

    @ameasure_time
    async def transcribe_media(self, file):
        async with aiofiles.tempfile.TemporaryDirectory() as directory:
            task = asyncio.create_task(
                self.__do_request(
                    audio_file_path=file,
                    output_directory_path=directory,
                )
            )
            try:
                result = await task
                insighter_logger.info("Successfully transcribe text")
                return result
            except Exception as e:
                insighter_logger.exception(e)

    async def __do_request(
            self,
            audio_file_path: str,
            output_directory_path: aiofiles.tempfile.TemporaryDirectory,
    ):
        try:
            slice_task = asyncio.create_task(
                self.__media_file_manager.process_audio_segments(
                    audio_file_path=audio_file_path,
                    output_directory_path=output_directory_path,
                )
            )
            files: list[str] = await slice_task
            tasks = []
            for file in files:
                tasks.append(asyncio.create_task(self.whisper_client.whisper_compile(file_path=file)))
            try:
                result = await asyncio.gather(*tasks)
                total_transcription = " ".join(result)
                return total_transcription
            except Exception as e:
                insighter_logger.exception(f"Failed to manage async transcribe. Exception {e}")
                raise AsyncTranscribitionError("Faild to manage async trancribe", exception=e) from e
        except Exception as e:
            insighter_logger.exception(f"Failed to transcribe: {e}")
            return ""


class MediaRecognitionFactory:
    def __init__(
            self,
            media_file_manager: MediaFileManager,
            short_media_transcriber: ShortMediaFilesTranscriber,
            long_media_transcriber: LongMediaFilesTranscriber,
    ):
        self.__media_file_manager = media_file_manager
        self.__long_media_transcriber = long_media_transcriber
        self.__short_media_transcriber = short_media_transcriber

    async def compile_transcription(self, file_path: str) -> str:
        """
        Return text
        :param file_path:
        :return:
        """

        try:
            request_method = await self.__factory_method(file_path=file_path)
            result = await request_method.transcribe_media(file=file_path)
            insighter_logger.info("successful transcribe text")
            return result
        except Exception as e:
            insighter_logger.exception(f"Failed to make request, exception is: {e}")
            raise TranscribitionError(exception=e) from e
 #TODO Заменить фабрику на один метод сейчкас это быстрая починка костыль
    async def __factory_method(self, file_path: str) -> MediaFileTranscriber:
        audio_size = await self.__media_file_manager.get_file_size_mb(file_path)
        insighter_logger.info(f'file size {audio_size}')
        # TODO вынести настройки размера модеоли
        if audio_size < 24:
            try:
                return self.__long_media_transcriber
            except Exception as e:
                insighter_logger.exception(f"faild to load class of long trancriber {e}")
                raise LoadingShorthandsTranscriberError(exception=e) from e
        elif audio_size >= 24:
            try:
                return self.__long_media_transcriber
            except Exception as e:
                insighter_logger.exception(f"faild to load class of long trancriber {e}")
                raise LoadingLongTranscriberError(exception=e) from e
        else:
            raise MediaSizeError(message="File size equal 0")
