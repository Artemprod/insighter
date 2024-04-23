import asyncio
from functools import partial

from pytube import YouTube
import os


def download_audio(url, path='/'):
    try:
        yt = YouTube(url)
        #TODO обернуть не всю функцию а только часть которую необходмо сделать декоратором
        audio_stream = yt.streams.get_audio_only()
        output_file = audio_stream.download(output_path=path)
        return os.path.normpath(output_file)
    except Exception as e:
        print("Произошла ошибка при загрузке аудио:", e)



def get_duration(url):
    try:
        yt = YouTube(url)
        return yt.length
    except Exception as e:
        print(e)


async def download_youtube_audio(url, path='/'):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            partial(download_audio, url, path, ),
        )
        return result
    except Exception as e:
        print(f"Failed to download: {e}")
        return None


async def get_youtube_audio_duration(url):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            partial(get_duration, url, ),
        )
        return result
    except Exception as e:
        print(f"Failed to get duration: {e}")
        return None


# Пример использования
if __name__ == "__main__":

    async def main():
        video_url = input("Введите URL видео с YouTube: ")
        destination_folder = input("Введите путь к папке для сохранения (оставьте пустым для текущей директории): ")
        if not destination_folder:
            destination_folder = './'  # Текущая директория
        tasks = asyncio.gather(download_youtube_audio(video_url, destination_folder), get_youtube_audio_duration(video_url))
        result = await tasks
        print(result)

    asyncio.run(main())

