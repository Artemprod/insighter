import json
import os.path
from os import path

import vosk
from pydub import AudioSegment

from logging_module.log_config import insighter_logger

model_dir = os.path.abspath("models")

model_path = path.normpath(path.join(model_dir, "vosk-model-small-ru-0.22"))
model = vosk.Model(model_path)
samplerate = 16000



def voice_message_recognition(voice_message_path):
    try:
        # Прямое открытие файла MP3
        audio = AudioSegment.from_mp3(voice_message_path)
    except Exception as e:
        insighter_logger.info("Ошибка загрузки аудиофайла:", str(e))
        return

    # Преобразование аудио в одноканальный (моно) WAV с нужной частотой дискретизации
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(samplerate)
    audio_data = audio.raw_data

    # Инициализация распознавателя Vosk
    rec = vosk.KaldiRecognizer(model, samplerate)

    # Обработка аудио порциями
    chunk_size = 4096  # размер порции в байтах
    for chunk in range(0, len(audio_data), chunk_size):
        rec.AcceptWaveform(audio_data[chunk : chunk + chunk_size])

    # Получение результатов распознавания
    result = json.loads(rec.FinalResult())
    recognized_text = result.get("text", "")

    return recognized_text


if __name__ == "__main__":
    a = voice_message_recognition(r"/text/3979 Продакт-менеджмент.mp3")
  
