FROM python:3.11

# Копируем весь проект в контейнер
COPY . .


RUN apt-get update -y && apt-get upgrade -y && apt-get install nano -y && pip install --upgrade pip  \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt && apt-get install -y ffmpeg \
    && apt-get clean

RUN python3 -c "import torch"

ENV PYTHONPATH $PYTHONPATH:.

CMD ["python3", "bot.py"]