import asyncio
import os
from functools import partial

from pydub import AudioSegment

from logging_module.log_config import insighter_logger
from main_process.file_format_manager import FileFormatDefiner


class MediaFileManager:
    export_format_for_chunks = 'mp3'

    def __init__(self, file_format_manager: FileFormatDefiner):
        self.__format_manager = file_format_manager

    @staticmethod
    async def get_file_size_mb(file_path):
        """
        Определяет размер файла в мегабайтах.

        Args:
        file_path (str): Путь к файлу.

        Returns:
        float: Размер файла в мегабайтах.
        """
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)  # Преобразование из байтов в мегабайты
        return size_mb

    async def export_segment_async(self, segment, saving_path, ):
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                partial(
                    self.export_segment,
                    segment,
                    saving_path,

                ),
            )
            return result
        except Exception as e:
            insighter_logger.exception(f"Failed to export segment: {e}")
            return None

    @staticmethod
    def export_segment(
            segment,
            saving_path
    ):
        try:

            segment.export(saving_path, format=MediaFileManager.export_format_for_chunks)
            insighter_logger.info(f"Exported segment to {saving_path}")
            return saving_path
        except Exception as e:
            insighter_logger.exception(e)
            insighter_logger.info(e, "Error export")

    async def process_audio_segments(self,
                                     audio_file_path,
                                     output_directory_path,
                                     ):
        media_format = await self.__format_manager.define_format(file_path=audio_file_path)
        insighter_logger.info(media_format)
        audio = AudioSegment.from_file(audio_file_path, format=media_format)
        semaphore = asyncio.Semaphore(10)  # Control concurrency
        segment_length = 10 * 60 * 1000  # 10 minutes in milliseconds
        tasks = [
            self.limit_task(
                semaphore,
                self.export_segment_async,
                audio[i: i + segment_length],
                os.path.join(
                    output_directory_path,
                    f"chunk_{i // segment_length}.{MediaFileManager.export_format_for_chunks}",

                ),
            )
            for i in range(0, len(audio), segment_length)
        ]

        return await asyncio.gather(*tasks)

    @staticmethod
    async def limit_task(semaphore,
                         func,
                         *args,
                         **kwargs):
        async with semaphore:
            result = await func(*args, **kwargs)
            return result
