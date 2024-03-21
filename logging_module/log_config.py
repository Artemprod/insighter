from environs import Env
from logtail import LogtailHandler
from loguru import logger
from notifiers.logging import NotificationHandler


def load_loguru():
    env: Env = Env()
    env.read_env(".env")
    logtail_source_token = env("LOGTAIL_INSIGTER_SOURCE")

    alert_bot_token = env("LOGER_BOT_TOKEN")
    telegram_notifiers_chat_ids = [int(chat_id) for chat_id in env("TELEGRAM_CHAT_IDS").split(",")]

    for chat_id in telegram_notifiers_chat_ids:
        params = {
            "token": alert_bot_token,
            "chat_id": chat_id,
        }

        logger.add(NotificationHandler("telegram", defaults=params), level="ERROR")

    logtail_handler = LogtailHandler(source_token=logtail_source_token)
    logger.add(
        logtail_handler,
        format="{message}",
        level="INFO",
        backtrace=False,
        diagnose=False,
    )

    #
    # logger.add("debug.json", format="{time} {level} {message}", level="DEBUG",
    #            rotation="9:00", compression="zip", serialize=True)
    return logger


insighter_logger = load_loguru()

if __name__ == "__main__":

    def divide(a, b):
        insighter_logger.info("Старт функции", divide.__name__)
        return a / b

    def main():
        insighter_logger.info("Старт функции", main.__name__)
        try:
            divide(1, 0)
        except ZeroDivisionError:
            insighter_logger.exception("Деление на нноль")

    main()
