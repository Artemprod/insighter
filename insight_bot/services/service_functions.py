import asyncio
import io
import os
from datetime import datetime
from typing import Callable

import aiofiles
import docker as docker
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, FSInputFile, Audio
from aiogram import Bot
import tarfile

from DB.Mongo.mongo_db import MongoAssistantRepositoryORM
from DB.Mongo.mongo_enteties import Assistant
from api.gpt import GPTAPIrequest
import os
import shutil



def get_relative_path(path):
    """
  Возвращает относительный путь от корня до указанного пути.

  Args:
    path: Полный путь к файлу или каталогу.

  Returns:
    Относительный путь.
  """

    parts = path.split("/")
    return "/".join(parts[len(parts) - 1:])


# async def get_media_file(data_from_income_message: Message, bot: Bot, container_id:str) -> str | None:
#     file_id = None
#     if data_from_income_message.content_type == ContentType.VOICE:
#         file_id = data_from_income_message.voice.file_id
#     elif data_from_income_message.content_type == ContentType.AUDIO:
#         file_id = data_from_income_message.audio.file_id
#
#     elif data_from_income_message.content_type == ContentType.DOCUMENT:
#         file_id = data_from_income_message.document.file_id
#         file = await bot.get_file(file_id)
#         file_path = file.file_path
#         return file_path
#     if file_id is None:
#         await data_from_income_message.reply("Формат файла не поддерживается.")
#         return None
#
#     file = await bot.get_file(file_id)
#     file_path = file.file_path
#
#     user_media_dir = os.path.join('media', 'user_media_files')
#     os.makedirs(user_media_dir, exist_ok=True)
#     # Путь куда будет сохранен файл на локальном диске
#     file_on_disk = os.path.join(user_media_dir, f"{file_id}.mp3")
#     print()
#     # Сохраняем файл
#     # file_name = await copy_file_from_container(container_id=container_id, container_file_path=file_path,
#     #                                            host_file_path=file_on_disk)
#     file_name = await copy_file_from_shared_volume(container_file_path=file_path,
#                                                host_file_path=file_on_disk)
#     print()
#
#     return os.path.normpath(os.path.join(user_media_dir, f"{file_name}"))


async def get_media_file_path(user_media_dir: str, file_id: str, file_extension: str) -> str:
    os.makedirs(user_media_dir, exist_ok=True)
    return os.path.join(user_media_dir, f"{file_id}.{file_extension}")


async def download_media_file(bot: Bot, file_path: str, destination: str) -> str:
    await bot.download_file(file_path, destination=destination)
    return destination


async def remove_file_async(file_path):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, os.remove, file_path)

async def ensure_directory_exists(path):
    print(f"Проверка наличия каталога: {path}")
    if not os.path.exists(path):
        print(f"Каталог не найден. Создание каталога: {path}")
        os.makedirs(path, exist_ok=True)
    else:
        print(f"Каталог уже существует: {path}")

async def get_media_file(data_from_income_message: Message, bot: Bot) -> str | None:
    file_id = None
    print("Определение типа контента сообщения...")
    if data_from_income_message.content_type == ContentType.VOICE:
        file_id = data_from_income_message.voice.file_id
    elif data_from_income_message.content_type == ContentType.AUDIO:
        file_id = data_from_income_message.audio.file_id
    elif data_from_income_message.content_type == ContentType.DOCUMENT:
        file_id = data_from_income_message.document.file_id

    print(f"file_id: {file_id}")
    if file_id is None:
        print("Формат файла не поддерживается.")
        await data_from_income_message.reply("Формат файла не поддерживается.")
        return None

    print("Получение объекта файла из Telegram...")
    file = await bot.get_file(file_id)
    file_path = file.file_path
    print(f"Путь к файлу в Telegram API: {file_path}")

    # Путь к файлу в общем томе shared_volume
    shared_file_path = os.path.join('/shared_data', os.path.basename(file_path))
    print(f"Путь к файлу в общем томе: {shared_file_path}")

    # Путь для локального сохранения файла в контейнере
    local_media_dir = '/media/user_media_files'
    print(f"Убеждаемся, что локальный каталог для медиа файлов существует: {local_media_dir}")
    await ensure_directory_exists(local_media_dir)
    local_file_path = os.path.join(local_media_dir, os.path.basename(file_path))
    print(f"Локальный путь к файлу для сохранения: {local_file_path}")

    # Проверяем существование файла в общем volume и копируем если есть
    print(f"Проверка наличия файла в общем томе: {shared_file_path}")
    if os.path.exists(shared_file_path):
        print("Файл найден. Начинаем копирование...")
        # Потоковое копирование файла
        async with aiofiles.open(shared_file_path, 'rb') as src, aiofiles.open(local_file_path, 'wb') as dst:
            while True:
                data = await src.read(64 * 1024)  # Читаем кусками по 64КБ
                if not data:
                    break
                await dst.write(data)
        print(f"Файл скопирован в {local_file_path}")
        print(f"Удаление файла из общего тома: {shared_file_path}")
        os.remove(shared_file_path)
        print(f"Удаление исходного файла: {file_path}")
        os.remove(file_path)
        return local_file_path
    else:
        print("Файл в общем томе не найден.")
        await data_from_income_message.reply("Файл не найден в общем томе.")
        return None

# async def copy_file_from_shared_volume(container_file_path, host_file_path):
#     try:
#         # Проверка наличия файла в общем volume
#         if not os.path.exists(container_file_path):
#             raise FileNotFoundError(f"File {container_file_path} not found")
#
#         # Копирование файла
#         shutil.copy(container_file_path, host_file_path)
#
#         # Удаление файла из общего volume
#         os.remove(container_file_path)
#
#         # Возвращаем имя скопированного файла
#         return os.path.basename(host_file_path)
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
#         return None


# async def copy_file_from_container(container_id, container_file_path, host_file_path):
#     client = docker.from_env()
#     try:
#         # Получение контейнера
#         container = client.containers.get(container_id)
#
#         # Получение файла из контейнера
#         bits, _ = container.get_archive(container_file_path)
#
#         # Открытие tar-архива из потока битов
#         file_obj = io.BytesIO()
#         for chunk in bits:
#             file_obj.write(chunk)
#         file_obj.seek(0)
#
#         extracted_file_name = None
#         with tarfile.open(fileobj=file_obj, mode='r') as tar:
#             # Извлечение файла из архива
#             for member in tar.getmembers():
#                 if member.isfile():
#                     extracted_file_name = member.name
#                     tar.extract(member, path=os.path.dirname(host_file_path))
#
#         # Удаление файла из контейнера после его копирования
#         container.exec_run(f'rm {container_file_path}')
#
#         # Возвращаем имя извлеченного файла
#         return extracted_file_name
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")
#         return None


# def get_container_id_by_service_name(service_name):
#     client = docker.from_env()
#     # Предполагается, что имя проекта - это имя каталога, где находится ваш docker-compose.yml
#     project_name = "insighter"
#     container_name_pattern = f"{project_name}_{service_name}_"
#
#     for container in client.containers.list():
#         if container_name_pattern in container.name:
#             return container.id
#     return None

async def load_assistant(state: FSMContext,
                         Gpt_assistant: GPTAPIrequest,
                         assistant_repo: MongoAssistantRepositoryORM) -> GPTAPIrequest:
    data = await state.get_data()
    assistant_id = data.get('assistant_id')
    asisitent_prompt: Assistant = await assistant_repo.get_one_assistant(assistant_id=assistant_id)
    Gpt_assistant.system_assistant = asisitent_prompt
    return Gpt_assistant


async def gen_doc_file_path(media_folder: str, sub_folder: str, message_event: Message) -> str:
    doc_directory = os.path.join(media_folder, sub_folder)
    doc_filename = f'{message_event.chat.id}_{datetime.now().strftime("%d_%B_%Y_%H_%M_%S")}.txt'
    doc_path = os.path.join(doc_directory, doc_filename)
    os.makedirs(doc_directory, exist_ok=True)
    return doc_path


async def generate_text_file(content: str, message_event: Message) -> tuple:
    file_name = f'{message_event.chat.id}_{datetime.now().strftime("%d_%B_%Y_%H_%M_%S")}.txt'
    # Кодируем содержимое в байты
    file_bytes = content.encode('utf-8')
    return file_bytes, file_name


async def form_content(summary: str, transcribed_text: str) -> str:
    return f'Самари:\n {summary} \n\n Транскрибация аудио:\n {transcribed_text}'


async def estimate_transcribe_duration(audio: Audio):
    async def estimate_download_file_duration() -> float:
        file_size = audio.file_size / (1024 * 1024)
        if file_size > 30:
            second_per_mb = 6
        else:
            second_per_mb = 3
        return file_size / second_per_mb if file_size > 0 else file_size * second_per_mb

    async def estimate_transcribe_file_duration() -> float:
        second_per_second = 12
        prediction = audio.duration / second_per_second

        return prediction

    download_file_duration = await estimate_download_file_duration()
    transcribe_duraton = await estimate_transcribe_file_duration()

    return int((download_file_duration + transcribe_duraton + 6) * 0.9)


async def estimate_gen_summary_duration(count_tokens: Callable, text: str) -> int:
    tokens = await count_tokens(encoding_name="cl100k_base", string=text)
    token_per_second = 13
    return int((tokens / token_per_second) * 0.5)


if __name__ == '__main__':

    # Пример использования функции
    container_id = "bf88eef88779"
    container_file_path = "/var/lib/telegram-bot-api/6970555880:AAFrBj3go_TXClpcQzDOs50DwHCFAUD6QlM/music/file_3.mp3"
    host_file_path = r"C:\Users\artem\OneDrive\Рабочий стол\text\file_3.mp3"

    # if copy_file_from_container(container_id, container_file_path, host_file_path):
    #     print("Файл успешно скопирован.")
    # else:
    #     print("Ошибка копирования файла.")
