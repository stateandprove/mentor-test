import json
import telebot

from datetime import datetime


# токен для телеграма - это секрет, а секреты всегда хранятся вне кода, обычно
# в переменных окружения, но мы для простоты используем текстовый файл с токеном
token_file = open('token.txt')
token = token_file.read()
token_file.close()

# будем хранить спящих юзеров и время когда они заснули в словаре
sleeping_users = dict()

# инициализация бота
bot = telebot.TeleBot(token)


# функция читает лог-файл и преобразует его в словарь
def load_sleeping_records_log() -> dict:
    # открываем файл, если его нет - создаем
    try:
        sleeping_records_log_file = open('sleeping_log.json', 'r')
    except FileNotFoundError:
        sleeping_records_log_file = open('sleeping_log.json', 'a+')

    # если файл пуст, используем пустой строковый json
    sleeping_records_log_str = sleeping_records_log_file.read() or "{}"
    sleeping_records_log = json.loads(sleeping_records_log_str)
    sleeping_records_log_file.close()

    return sleeping_records_log


# запись в лог файл
def write_to_sleeping_records_log(data: dict) -> None:
    sleeping_records_log_file = open('sleeping_log.json', 'w')
    json.dump(data, sleeping_records_log_file, indent=4, ensure_ascii=False)
    sleeping_records_log_file.close()


# по заданному ключу эта функция обновляет последнюю запись в лог файле для
# заданного юзера; вернет True в случае успешного апдейта и False в обратном
def update_last_sleeping_record(user_id: str | int, key: str, value: str) -> bool:
    records_log = load_sleeping_records_log()
    user_records_history = records_log.get(str(user_id))

    if not user_records_history:
        return False

    last_user_record = user_records_history[-1]
    last_user_record[key] = value
    write_to_sleeping_records_log(records_log)

    return True


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    msg = (
        "Привет! Я буду помогать тебе отслеживать параметры сна. "
        "Используй команды /sleep, /wake, /quality и /note."
    )
    bot.reply_to(message, msg)


@bot.message_handler(commands=['sleep'])
def handle_sleep(message):
    if sleeping_users.get(message.from_user.id):
        bot.reply_to(message, "Я уже получил команду /sleep!")
        return

    # запоминаем юзера и время, когда он лег спать
    sleeping_users[message.from_user.id] = datetime.now()

    msg = "Спокойной ночи! Не забудь сообщить мне, когда проснешься командой /wake."
    bot.reply_to(message, msg)


@bot.message_handler(commands=['wake'])
def handle_wake(message):
    # проверяем, есть ли юзер среди заснувших и получаем время, когда он заснул
    time_felt_asleep_at = sleeping_users.get(message.from_user.id)

    if not time_felt_asleep_at:
        # если нету, то пишем об этом юзеру и завершаем работу функции
        msg = "Я не вижу сообщения о начале сна. Используй команду /sleep."
        bot.reply_to(message, msg)
        return

    # рассчитываем продолжительность сна
    sleep_duration = datetime.now() - time_felt_asleep_at
    total_seconds = int(sleep_duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)  # деление с остатком
    minutes = remainder // 60  # полное число минут в остатке

    # убираем юзера из числа спящих
    sleeping_users.pop(message.from_user.id)

    # формируем запись
    sleeping_record = {
        "time_felt_asleep_at": time_felt_asleep_at.isoformat(),
        "sleep_duration": total_seconds,
        "quality": None,
        "note": ""
    }

    # открываем лог файл и получаем историю записей для пользователя
    sleeping_records_log = load_sleeping_records_log()
    user_sleeping_records = sleeping_records_log.get(str(message.from_user.id))

    if not user_sleeping_records:
        # если истории у юзера нет - создадим ее
        sleeping_records_log[message.from_user.id] = []
        user_sleeping_records = sleeping_records_log[message.from_user.id]

    # добавляем запись в историю и обновляем файл
    user_sleeping_records.append(sleeping_record)
    write_to_sleeping_records_log(sleeping_records_log)

    msg = (
        f"Доброе утро! Продолжительность сна составила {hours} ч. {minutes} мин. Не забудь"
        " оценить качество сна командой /quality и оставить заметки командой /note."
    )
    bot.reply_to(message, msg)


# quality и note делают одно и то же - по ключу обновляют значение,
# поэтому объединим их в одну функцию
@bot.message_handler(commands=['quality', 'note'])
def handle_quality_note(message):
    # парсим ввод юзера
    user_input_split = message.text.split(" ")

    # при пустом значении ввода выдаем ошибку
    if len(user_input_split) < 2:
        bot.reply_to(message, "Неверный формат ввода!")
        return

    # получаем первый аргумент и убираем слеш - это наш ключ, значение - все остальное
    key = user_input_split[0][1:]
    value = " ".join(user_input_split[1:])

    # обновляем последнюю запись
    record_updated = update_last_sleeping_record(message.from_user.id, key, value)

    if not record_updated:
        bot.reply_to(message, "У тебя еще нету ни одной записи!")
        return

    bot.reply_to(message, "Спасибо за оценку качества сна!")


bot.infinity_polling()
