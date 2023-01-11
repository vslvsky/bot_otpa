import datetime
import sys
from datetime import datetime

import requests

import DataBase as dbase
import VitalityBooster as vb
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import telebot
import time
import json
import os

from my_token import token
from my_token import chat_id


warnings.filterwarnings('ignore')
bot = telebot.TeleBot(token)


select_1hours = """select  closing_user,
        count(terrasoft_number)
            from terrasoft.incidents i 
  where end_date >= current_timestamp - INTERVAL '1 hour' 
    and terrasoft_code in   ('602ф Не работает интернет',
							'604-1ф Прерывание сервиса (потеря пакетов)',
							'604-2ф Высокий пинг',
							'604ф Низкая скорость',
							'606-1ф Не доступен сторонний ресурс',
							'606ф Не работает сайт sibset',
							'614 Не работает антивирус',
							'615-2 Не получает плейлист',
							'615-3 Не работает канал',
							'615-4 Зависает/рассыпается изображение',
							'615-6 Не работает архив',
							'615-7 Не совпадает/отсутствует программа телепередач',
							'615 Не работает IPTV',
							'616-2 Не включается приставка',
							'616-3 Самостоятельно перезагружается',
							'616-4 Не работает приложение youtube, погода, пробки и т.д.',
							'616-5 Не подключается wi-fi',
							'616 Проблема с приставкой IPTV',
							'617ф Не работает телефония',
							'618 Проблема с Видеотекой/Кинозал',
							'622 Ошибка с приложением Лайк ТВ',
							'623ф Настройка роутера/компьютера',
							'630 - Не работает мобильное приложение',
							'635-1 Не работает приложение Умный домофон',
							'635-3 Авария по Умному домофону (подъезд)',
							'635-4ф Проблемы с архивом ДУ',
							'635-5ф Недоступна история вызовов ДУ',
							'635-6ф Не работает камера ДУ',
							'635-8ф Не идет вызов на телефон из ДУ',
							'642 VLAN',
							'706ф Заявка на белый IP',
							'713-3ф Подключение дополнительной камеры видеонаблюдения (двор) без УД',
							'714ф Прописать')
		group by 1
		order by 2 desc"""
select_today = """select  closing_user,
        count(terrasoft_number)
            from terrasoft.incidents i 
  where end_date >= current_date
    and terrasoft_code in   ('602ф Не работает интернет',
							'604-1ф Прерывание сервиса (потеря пакетов)',
							'604-2ф Высокий пинг',
							'604ф Низкая скорость',
							'606-1ф Не доступен сторонний ресурс',
							'606ф Не работает сайт sibset',
							'614 Не работает антивирус',
							'615-2 Не получает плейлист',
							'615-3 Не работает канал',
							'615-4 Зависает/рассыпается изображение',
							'615-6 Не работает архив',
							'615-7 Не совпадает/отсутствует программа телепередач',
							'615 Не работает IPTV',
							'616-2 Не включается приставка',
							'616-3 Самостоятельно перезагружается',
							'616-4 Не работает приложение youtube, погода, пробки и т.д.',
							'616-5 Не подключается wi-fi',
							'616 Проблема с приставкой IPTV',
							'617ф Не работает телефония',
							'618 Проблема с Видеотекой/Кинозал',
							'622 Ошибка с приложением Лайк ТВ',
							'623ф Настройка роутера/компьютера',
							'630 - Не работает мобильное приложение',
							'635-1 Не работает приложение Умный домофон',
							'635-3 Авария по Умному домофону (подъезд)',
							'635-4ф Проблемы с архивом ДУ',
							'635-5ф Недоступна история вызовов ДУ',
							'635-6ф Не работает камера ДУ',
							'635-8ф Не идет вызов на телефон из ДУ',
							'642 VLAN',
							'706ф Заявка на белый IP',
							'713-3ф Подключение дополнительной камеры видеонаблюдения (двор) без УД',
							'714ф Прописать')
		group by 1
		order by 2 desc"""


def get_datatime() -> datetime:
    date_format = '%H:%M:%S %d.%m.%Y'
    today = datetime.now()
    today = today.strftime(date_format)
    return today


def get_dataframe(select_sql) -> dict:
    dl = vb.MessengerSQL(dbase.PostgreSQL_Datalake())
    dl.connect()
    dataframe = dl.send_command(select_sql)
    return dataframe


def do_chart(*, dataframe: dict, name: str, title: str, y: str, x: str) -> object:
    """Создает столбиковый график из вводных данных, с помощью библиотеки seaborn
     и затем сохраняет в формате .png с названием 'name.png'"""
    color = sns.color_palette('Reds_r', 23)

    sns.set()
    plt.figure()

    ax = sns.barplot(data=dataframe, y=y, x=x, palette=color)
    ax.set_title(title)
    ax.grid(color='#cccccc')
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    plt.tight_layout()
    plt.savefig(f"{os.getcwd()}\{name}.png")


def main():

    try:
        with open(f"{os.getcwd()}/message_history.txt") as json_file:
            message_history = json.load(json_file)

        for message in message_history:
            bot.delete_message(chat_id, message['id'])
    except Exception:
        pass
    finally:
        message_history = [] #или очищаем файл или создаем новый

    for index in range(5):
        try:
            if get_dataframe(select_1hours).empty:
                if get_dataframe(select_today).empty:
                    message = bot.send_message(chat_id, f"По данным на {get_datatime()} закрытых инцедентов нет")
                    message_history.append({
                        'date': get_datatime(),
                        'id': message.id
                    })
                else:
                    # график "сегодня"
                    do_chart(dataframe=get_dataframe(select_today), name="closing_today", title=f"Закрытые инциденты за сегодня\n{get_datatime()}", y="closing_user", x="count")
                    photo_today = open(f"{os.getcwd()}/closing_today.png", 'rb')
                    message = bot.send_photo(chat_id, photo_today)
                    message_history.append({
                        'date': get_datatime(),
                        'id': message.id
                    })
            else:
                #график "1 час"
                do_chart(dataframe=get_dataframe(select_1hours), name="closing_1hour", title=f"Закрытые инциденты за 1 час\n{get_datatime()}", y="closing_user", x="count")
                photo_1hour = open(f"{os.getcwd()}/closing_1hour.png", 'rb')
                message = bot.send_photo(chat_id, photo_1hour)
                message_history.append({
                    'date': get_datatime(),
                    'id': message.id
                })
                #график "сегодня"
                do_chart(dataframe=get_dataframe(select_today), name="closing_today", title=f"Закрытые инциденты за сегодня\n{get_datatime()}", y="closing_user", x="count")
                photo_today = open(f"{os.getcwd()}/closing_today.png", 'rb')
                message = bot.send_photo(chat_id, photo_today)
                message_history.append({
                    'date': get_datatime(),
                    'id': message.id
                })
            break
        except requests.ConnectionError:
            time.sleep(2)
    with open(f"{os.getcwd()}/message_history.txt", 'w') as outfile:
        json.dump(message_history, outfile)


if __name__ == '__main__':
    main()
    # try:
    #     main()
    #
    #     vb.send_successfully('otpa_infobot')
    # except requests.ConnectionError:
    #     pass
    # except Exception as exception:  # ZeroDivisionError Exception
    #     vb.send_error(exception, 'otpa_infobot')