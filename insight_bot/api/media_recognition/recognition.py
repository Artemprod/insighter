import datetime
import logging
from datetime import time
import time
import tiktoken
from mutagen import File
import openai
import vosk
import whisper
import json
import os
from pydub import AudioSegment

import asyncio

from config.bot_configs import load_bot_config


class MediaRecognition:
    async def transcribe_file(self, file_path):
        raise NotImplementedError('Method transcribe_file() must be implemented asynchronously')

    async def del_temp_files(self):
        raise NotImplementedError('Method transcribe_file() must be implemented asynchronously')



class WhisperRecognition(MediaRecognition):

    def __init__(self, model='base'):
        self.model = whisper.load_model(model)

    async def transcribe_file(self, file_path) -> str:
        result = self.model.transcribe(file_path)
        print(result["text"])
        return result["text"]


class WhisperRecognitionAPI(MediaRecognition):
    gpt_model_3: str = "gpt-3.5-turbo-1106"
    gpt_model_4: str = "gpt-4"
    gpt_model_3_16: str = "gpt-3.5-turbo-16k-0613"
    whisper_model = "whisper-1"
    api_key = None
    # output_folder = r"D:\python projects\non_comertial\insighter\insight_bot\api\media_recognition\temp_files"
    output_folder = os.path.normpath(os.path.abspath('temp_files'))

    def __init__(self):
        openai.api_key = WhisperRecognitionAPI.api_key
        self.bad_word_prompt = "Эм..Ага, так, да,да..."
        self.punctuation_prompt = "Добрый день, спасибо что пришли! Сегодня..."
        self._load_api()

    @classmethod
    def _load_api(cls):
        """Загружает api key для класса, при условии что ключь находиться в env"""
        if cls.api_key is None:
            cls.api_key = load_bot_config('.env').ChatGPT.key
            logging.info("API ключ загружен.")

    async def transcribe_file(self, file_path) -> str:
        """в зависимости от длинны входящего файла либо нарезает либо делает сразу запрос"""

        start_time = time.time()
        audio_size = await self.get_file_size_mb(file_path)
        if audio_size > 24:
            result = await self.transcribe_large_files(file_path)

            end_time = time.time()
            logging.info("время транспирации:", end_time - start_time)
            print("время транспирации:", end_time - start_time)
            logging.info("Текст транспирации:\n", result)
            print(f"Время выполнения: {end_time - start_time} секунд")
            return result

        result = await self.get_api_request(file_path)
        logging.info(result)
        end_time = time.time()
        logging.info("время транспирации:", end_time - start_time)
        print(f"Время выполнения: {end_time - start_time} секунд")
        return result

    async def del_temp_files(self):
        files = os.listdir(self.output_folder)
        for file in files:
            path = f'{self.output_folder}/{file}'
            try:
                os.remove(path)
                logging.info("файл удален:", path)
            except Exception as e:
                logging.error(e, "Ошибка удаления файла")

    async def get_api_request(self, file_path, prompt=''):
        """Given a prompt, transcribe the audio file."""
        transcript = openai.audio.transcriptions.create(
            file=open(file_path, "rb"),
            model=WhisperRecognitionAPI.whisper_model,
            prompt=f'{self.punctuation_prompt}, {self.bad_word_prompt}, {prompt}',
        )
        return transcript.text

    async def transcribe_large_files(self, file_path) -> str:
        """Транскрибирует большие файлы, разбивая их на части.
            Для учета контекста используеться 224 последних токена для сохранения контекста
            для сохранения пунктуации в промпте используется фразы с запятыми
            для сохранения слов паразитов использовать в промпте "эм, да, ща..." и так далее
        """
        try:
            files = await self.slice_big_audio(file_path)
            total_transcription = ""
            for filename in files:
                file_path = os.path.normpath(os.path.join(WhisperRecognitionAPI.output_folder, filename))
                transcribed_text = await self.get_api_request(file_path=file_path, prompt=total_transcription[-500:])
                total_transcription += transcribed_text + "\n"
                logging.info("Кусок текста готов")
            return total_transcription
        except Exception as e:
            logging.error(f"Ошибка при транскрибации больших файлов: {e}")
            return ""

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

    async def define_format(self, file_path):
        """
            Определяет формат аудиофайла.

            Args:
            file_path (str): Путь к аудиофайлу.

            Returns:
            str: Формат файла.
            """
        audio = File(file_path)
        if audio is not None:
            return audio.mime[0].split('/')[1]  # Возвращает тип файла после '/'
        else:
            logging.info("Неизвестный формат")
            return "None"

    async def slice_big_audio(self, audio_file_path):
        """Разделяет большой аудифайл на куски и переводит вформат mp3"""
        list_of_otput_files = []
        format = await self.define_format(audio_file_path)
        audio = AudioSegment.from_file(audio_file_path, format=format)
        segment_length = 10 * 60 * 1000
        if not os.path.exists(WhisperRecognitionAPI.output_folder):
            os.makedirs(WhisperRecognitionAPI.output_folder)

        # Разделите и экспортируйте аудио на сегменты
        for i in range(0, len(audio), segment_length):
            segment = audio[i:i + segment_length]
            chunk_file_name = f"chunk_{i // segment_length}.mp3"
            segment.export(os.path.join(WhisperRecognitionAPI.output_folder, chunk_file_name), format="mp3")
            list_of_otput_files.append(chunk_file_name)
        return list_of_otput_files

    @staticmethod
    async def num_tokens_from_string(string: str) -> int:
        """возвращает количесвто токенов в тексте """
        encoding = tiktoken.get_encoding(WhisperRecognitionAPI.gpt_model_3)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    async def cut_text(self, string, tokens):
        """
        Образеает в тексте все до последних n токенов не больше 224
        :param string:
        :param tokens:
        :return: string
        """
        ...


class VoskRecognition(MediaRecognition):
    samplerate = 16000
    model_path = None
    model = None

    @classmethod
    def load_model(cls, model_name='vosk-model-small-ru-0.22'):
        if cls.model is None:
            model_dir = os.path.normpath(os.path.abspath('vosk_model'))
            cls.model_path = os.path.normpath(os.path.join(model_dir, 'models', model_name))
            cls.model = vosk.Model(cls.model_path)

    def _transcribe(self, audio_data, ) -> str:
        rec = vosk.KaldiRecognizer(VoskRecognition.model, self.samplerate)

        chunk_size = 4096
        while True:
            chunk = audio_data[:chunk_size]
            audio_data = audio_data[chunk_size:]

            if len(chunk) == 0:
                break
            if not rec.AcceptWaveform(chunk):
                continue

        result = json.loads(rec.FinalResult())
        return result.get("text", "")

    def transcribe_file(self, file_path) -> str | None:
        VoskRecognition.load_model()  # Make sure the model is loaded

        try:
            audio = AudioSegment.from_mp3(file_path)
            audio = audio.set_channels(1).set_frame_rate(self.samplerate)
            audio_data = audio.raw_data
        except Exception as e:
            print("Ошибка загрузки аудиофайла:", e)
            return None
        # Выполнение блокирующего кода в фоновом потоке
        recognized_text = self._transcribe(audio_data)
        return recognized_text


async def main(file):
    asyncio.create_task(WhisperRecognitionAPI().transcribe_file(file))


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print()
    audio_path = r"C:\Users\artem\OneDrive\Рабочий стол\text\audio1830177390.m4a"
    # output_folder = r"C:\Users\artem\OneDrive\Рабочий стол\text\chunks"
    asyncio.run(main(audio_path))
