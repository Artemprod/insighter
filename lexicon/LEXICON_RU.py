LEXICON_RU: dict = {
    "description": """
Привет! 
Познакомься с <b>Insighter</b> – твоим новым помощником в мире деловых коммуникаций.

Тратишь время, чтобы разобраться в записках, сделанных во время переговоров?
Переслушиваешь записи встреч, чтобы составить фоллоу-ап, найти нужную информацию или не забыть об упомянутых задачах?

Чат-бот Insighter сформирует <i>короткие и содержательные выжимки</i> на основе записей встреч, тем самым <i>сэкономив</i> тебе кучу времени и усилий.

<b>Особенности Insighter:</b>
<b>•</b> транскрибирует записи встреч и звонков любой продолжительности;
<b>•</b> готовит резюме и фоллоу-апы встреч;
<b>•</b> упрощает принятие решений за счет консолидации ключевых аспектов встреч.

Insighter - твоя суперсила, которая позволит тратить драгоценное время только на содержательные задачи!

Воспользуйся кнопкой <i> "Меню" </i> или командами:

/start чтобы перезапустить бота;
/feedback чтобы оставить обратную связь или сообщить об ошибке;
/pay чтобы пополнить баланс минут;
/info чтобы прочесть информацию о сервисе.

Если что-то непонятно - напиши @blackgraf14
        """,
    "your_file": "<b>Вот твой документ с рекомендациями</b>",
    "next": "<b>Выбери сценарий обработки записи: </b>",
    "ready": "<b>Транскрибация завершена, сейчас сделаю анализ</b>",
    "instructions": """<b>Инструкция</b>\n
Для получения краткого содержания и полной расшифровки твоей онлайн встречи загрузи аудио или видеозапись. Вот поддерживаемые форматы:\n
<b>Аудио:</b> m4a, m4b, m4p, m4r, mp3, aac, ac3, wav, alac, flac, flv, wma, amr, mpga, ogg, oga, mogg, 8svx, aif, ape, au, dss, opus, qcp, tta, voc, wv
<b>Видео:</b> m4p, m4v, webm, mts, m2ts, ts, mov, mp2, mxf
<b>Ссылка на видео:</b> только https://www.youtube.com/\n
<b>Важно!</b>\n
<b>•</b> Рекомендуем обрабатывать записи продолжительностью не более 1 часа;\n
<b>•</b> Иногда могут происходить сбои в работе сервиса при одновременной обработке файлов большим количеством пользователей;\n
<b>•</b> Если не появились сообщения об обработке файлов, или прошло более 30 минут после загрузки файла, нажми команду /start
""",
    "documents_tittle": "<b>Вот твои документы</b>",
    "transcribed_document_caption": "Распознанный текст",
    "error_message": "Произошла непредвиденная ошибка. Необходимо перезапустить бота командой /start",
    "actual_formats": """
<b>Аудио:</b> m4a, m4b, m4p, m4r, mp3, aac, ac3, wav, alac, flac, flv, wma, amr, mpga, ogg, oga, mogg, 8svx, aif, ape, au, dss, opus, qcp, tta, voc, wv.
<b>Видео:</b> m4p, m4v, webm, mts, m2ts, ts, mov, mp2, mxf.
<b>Ссылка на видео:</b> формат https://www.youtube.com/
""",
    "wrong_format": """ 
Данный формат файла: "<i>{income_file_format}</i>", не поддерживается сервисом.

<b>Поддерживаемые форматы файлов:</b>\n
<b>Аудио:</b> m4a, m4b, m4p, m4r, mp3, aac, ac3, wav, alac, flac, flv, wma, amr, mpga, ogg, oga, mogg, 8svx, aif, ape, au, dss, opus, qcp, tta, voc, wv
<b>Видео:</b> m4p, m4v, webm, mts, m2ts, ts, mov, mp2, mxf
<b>Ссылка на видео:</b> только https://www.youtube.com/\n
Загрузи файл подходящего формата
""",

    "is_not_youtube_link": "Это {link} не ссылка на видео. Пришли правильную ссылку вида https://www.youtube.com/..."
}


LEXICON_ASSISTANTS: dict = {
    "client_service": {
        "name": "Аcсистент клиентской поддержки",
        "button_name": "Анализ звонка",
        "assistant_prompt": """Ты опытный руководитель отдела продаж образовательных онлайн курсов.""",
        "user_prompt": """Я сейчас пришлю файл с транскрипцией звонка менеджера отдела продаж. Необходимо выделить самое важное из диалога с клиентом и затем кратко ответить на несколько вопросов:
1. Состоялась ли продажа или были намечены следующие шаги с покупателем?
2. Выявлена ли потребность покупателя в продукте и какая она?
3. Отработаны ли возражения покупателя и какие они были: составь список всех возражений клиента?
4. Какой была общая эмоциональная составляющая диалога, не было ли негатива от покупателя?
5. Что можно порекомендовать менеджеру для более успешного и продуктивного ведения диалога с клиентом для закрытия сделки?
В конце напиши саммари по качеству работы менеджера отдела продаж и оцени работу по шкале от 1 до 10, где 10 высшая оценка.""",
    },
    "product_manager": {
        "name": "Асистент продатк менеджера ",
        "button_name": "Инсайт по интервью",
        "assistant_prompt": """Ты опытный senior product manager, который постоянно проводит и анализируем огромное количество проблемных интервью""",
        "user_prompt": """Сейчас я пришлю файл с расшифровкой проблемного интервью. Твоя задача выделить самое важное из ответов респондента, составить список ключевых проблем пользователя, составить список инсайтов.  В конце необходимо составить саммари этого проблемного интервью.""",
    },
    "secretary": {
        "assistant_prompt": """Вы занимаете позицию опытного секретаря в динамично развивающейся компании. Ваша роль охватывает не только традиционные задачи секретаря, но и более глубокий анализ деловых встреч. Вам доверяется задача тщательной фиксации всех ключевых моментов встреч, принятия важных решений и составления подробных сводок для руководства, чтобы они могли эффективно ориентироваться в динамике бизнес-процессов.""",
        "user_prompt": """Обязательно прочти полностью весь текст встречи от начала до конца. 
Тебе необходимо выделить самые важные моменты и договоренности из записи разговора на встрече. Обязательно учти реплики или цитаты собеседников после слов "важно" и т.д. Напиши саммари встречи и фоллоу-ап со всеми договоренностями собеседников. 
Никогда НЕ используй нумерованные списки и маркированные,  пиши каждую новую заметку с новой строки. Не используй цифры, цифры пиши словами""",
    },
    "total_summary": {
        "assistant_prompt": """Вы занимаете позицию опытного секретаря в динамично развивающейся компании. Ваша роль охватывает не только традиционные задачи секретаря, но и более глубокий анализ деловых встреч. Вам доверяется задача тщательной фиксации всех ключевых моментов встреч, принятия важных решений и составления подробных сводок для руководства, чтобы они могли эффективно ориентироваться в динамике бизнес-процессов.""",
        "user_prompt": """Вам предстоит проанализировать подробную запись последней значимой деловой встречи. Ваша основная цель — выявить и подчеркнуть фразы и утверждения, начинающиеся со слов 'важно' или аналогичных, которые указывают на критически важные моменты и решения. На основе этого анализа, вам необходимо составить всеобъемлющее, но сжатое резюме встречи, включающее в себя все ключевые пункты обсуждения. Кроме того, важно предложить четкие и конкретные рекомендации по каждому обсуждаемому вопросу, основываясь на выявленных в ходе встречи решениях и соглашениях. Ваша работа поможет руководству компании более эффективно планировать свои дальнейшие действия и стратегии, учитывая все нюансы обсуждаемых вопросов.""",
    },
}

LEXICON_COMMANDS: dict[str, str] = {
    "/start": "Перезапустить бот",
    "/feedback": "Оставить обратную связь",
    "/info": "Информация о сервисе",
    "/pay": "Пополнить баланс минут",
}
REFERRAL_MESSAGE = """
Пригласи нового пользователя в бота и получи 100 минут обработок записей бесплатно! 
Для этого необходимо:
1. Написать в личные сообщения Александру (@blackgraf14) имя приглашаемого пользователя;
2. Отправить ссылку на бота https://t.me/ai_insighter_bot приглашаемому пользователю;
3. Подождать пока приглашенный пользователь запустит бота кнопкой или командой /start
После выполнения всех условий будут начислены по 100 минут тебе и приглашенному пользователю.

<b>Важно:</b> 
1. Если пользователь уже использует бота, начисление минут не произойдет.
2. Если пользователь сменит свое имя в Telegram до старта бота, но после приглашения, начисление минут не произойдет.
3. Если кто-то раньше уже пригласил этого пользователя, начисление минут будет совершено тому, кто пригласил его раньше.
4. Приглашать можно любое количество пользователей.

Дополнительно можно получить еще 300 минут бесплатно, если рассказать о нашем продукте у себя в социальных сетях. 
<b>Для этого необходимо:</b>
1. Написать пост про наш сервис и прикрепить к нему ссылку на бота https://t.me/ai_insighter_bot
2. Сделать скриншот этого поста
3. Прислать Александру (@blackgraf14) личное сообщение со скриншотом и ссылкой на пост.
После проверки выполнения всех условий тебе будут начислены 300 минут обработок бесплатно.
"""
TIME_ERROR_MESSAGE = """
Не хватает {time} минут для обработки записи. 
Чтобы пополнить баланс, напиши личное сообщение Александру, воспользуйся реферальной программой или пополни пакет минут в разделе оплаты /pay
"""
TIME_ERROR_MESSAGE_MIDDLEWARE = """
Не хватает минут для обработки записей. 
Чтобы пополнить баланс, напиши личное сообщение Александру, воспользуйся реферальной программой или пополни пакет минут в разделе оплаты /pay
"""
TARIFFS: dict[str, str] = {
    "base": "base",
    "standard": "standard",
    "premium": "premium",
}

pre_buy_demo_alert = """\
Так как сейчас я запущен в тестовом режиме, для оплаты нужно использовать данные тестовой карты: 1111 1111 1111 1026 12/21 000 
"""

base_title = 'Оплата тарифа "Базовый" '
standard_title = 'Оплата  тарифа "Стандарт"'
premium_title = 'Оплата тарифа "Премиум"'

description = """\
Оплата и Пакеты Услуг Insighter
Чем больше минут в пакете, тем дешевле!
"""

base = """200 минут за 990₽ (4,95₽/мин)"""
standard = """400 минут за 1490₽ (3,72₽/мин)"""
premium = """2000 минут за 4950₽ (2,47₽/мин)"""

successful_payment = """
Ура! Платеж на сумму `{total_amount} {currency}` совершен успешно! Желаем приятного использования.
Оставить обратную связь - /feedback
Купить еще минут - /buy
Начать использовать - /start
"""
start_parameter = "insighter"
MESSAGES = {
    "pre_buy_demo_alert": pre_buy_demo_alert,
    "tm_description": description,
    "base_title": base_title,
    "standard_title": standard_title,
    "premium_title": premium_title,
    "base": base,
    "standard": standard,
    "premium": premium,
    "successful_payment": successful_payment,
    "start_parameter": start_parameter,
}
