import requests
import datetime
import numpy
import pandas as pd
from datetime import datetime, timedelta
import DataBase as dbase
import VitalityBooster as vb
import warnings
from prettytable import PrettyTable
import seaborn as sns
import matplotlib.pyplot as plt
import telebot
from my_token import token

warnings.filterwarnings('ignore')

url = f"https://api.telegram.org/bot{token}/sendMessage"

def get_datatime() -> datetime:
    date_format = '%H:%M:%S %Y.%m.%d'
    today = datetime.now() #- timedelta(days=1)
    today = today.strftime(date_format)
    return today


def send_message(text: str, chat_id: str, url: str) -> None:
    params = {'text': text,
              'chat_id': chat_id}
    requests.post(url=url, params=params)

def send_photo(photo, chat_id: str, url: str) -> None:
    params = {'photo': photo,
              'chat_id': chat_id}
    requests.post(url=url, params=params)


def get_dataframe(select_sql) -> dict:
    dl = vb.MessengerSQL(dbase.PostgreSQL_Datalake())
    dl.connect()
    dataframe = dl.send_command(select_sql)
    return dataframe

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



dataframe_1hour = get_dataframe(select_1hours)
header = ['closing_user', 'count']
table_closing_1hour = PrettyTable(vertical_char='-', junction_char='-', header=False, title='Кол-во закрытых за час')
table_closing_1hour.add_column("closing_user", dataframe_1hour['closing_user'].to_list())
table_closing_1hour.add_column("count", dataframe_1hour['count'].to_list())

dataframe_today = get_dataframe(select_today)
header = ['closing_user', 'count']
table_closing_today = PrettyTable(vertical_char='-', junction_char='-', header=False, title='Кол-во закрытых за сегодня')
table_closing_today.add_column("closing_user", dataframe_today['closing_user'].to_list())
table_closing_today.add_column("count", dataframe_today['count'].to_list())


# Some boilerplate to initialise things
sns.set()
plt.figure()

# This is where the actual plot gets made
ax = sns.barplot(data=dataframe_today, y="closing_user", x="count", saturation=0.6)


cities = ['Paris','Moscow','Rome','London']
values = [175,380,445,470]

#bars = plt.bar(cities, values)
#ax = plt.gca()

# Customise some display properties
ax.set_title('Закрытые инциденты за сегодня')
ax.grid(color='#cccccc')
ax.set_ylabel('Количество закрытых инцидентов')
ax.set_xlabel(None)
#ax.set_yticklabels(dataframe_today["closing_user"], figsize=(3,3))
#ax.text("test")


#ax.set_xticklabels(dataframe_today["count"].unique().astype(str), rotation='horizontal')
# Ask Matplotlib to show it
#plt.show()
plt.tight_layout()

plt.savefig('foo1.png')


url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"


text = f" \n На {get_datatime()} \n {table_closing_1hour} \n\n {table_closing_today}"

#chat_id = '@otpa_infobot'
chat_id = '1105837299'

bot = telebot.TeleBot(token)

photo = open('foo1.png', 'rb')
bot.send_photo(chat_id, photo)
bot.send_message(chat_id, 'test telebot')

def main():
    send_message(text, chat_id, url)



if __name__ == '__main__':
    main()
