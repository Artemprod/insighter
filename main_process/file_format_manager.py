
import asyncio

from abc import ABC, abstractmethod
from os import path

import filetype


from costume_exceptions.format_exceptions import UnknownFormatRecognitionError
from logging_module.log_config import insighter_logger


from main_process.func_decorators import ameasure_time


class FileFormatDefiner(ABC):
    @abstractmethod
    async def define_format(self, file_path) -> str:
        pass


class TelegramServerFileFormatDefiner(FileFormatDefiner):
    @ameasure_time
    async def define_format(self, file_path) -> str:
        file_path = path.normpath(file_path)
        kind_task = asyncio.create_task(
            self.__kind_define_format(file_path=file_path),
            name="define format by kind",
        )
        try:
            result = await kind_task
            return result

        except UnknownFormatRecognitionError:
            insighter_logger.info("kind_task failed to handle a work")
            insighter_logger.info("start simple string task...")
            string_task = asyncio.create_task(
                self.__simple_string_define_format(file_path=file_path),
                name="define format by simple string recogntion",
            )
            try:
                result = await string_task
                return result
            except UnknownFormatRecognitionError:
                insighter_logger.exception("all format methods are failed, try another")
                # TODO Добавить отправку сообщения что формат файла не подхиодит отправ



    @staticmethod
    async def __kind_define_format(file_path):
        kind = filetype.guess(file_path)
        if kind is None:
            insighter_logger.error("Unknown format ,kind cant managed to retrieve information ")
            raise UnknownFormatRecognitionError("Неизвестный формат")
        else:
            insighter_logger.info("successfully work of Kind \n\n File MIME type: %s" % kind.mime)
            return kind.extension

    @staticmethod
    async def __simple_string_define_format(file_path) -> str:
        file_name = file_path.split("\\")[-1]
        file_format = file_name.split(".")[-1]
        if file_format:
            return file_format
        raise UnknownFormatRecognitionError("cant find a proper format by string")
