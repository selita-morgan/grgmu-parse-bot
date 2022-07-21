import requests
from bs4 import BeautifulSoup as bs
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import logging
from datetime import datetime

TOKEN = '5396593007:AAHk7uU4ue6hOjEdH-pr3ouwaq2cN9vCwCU'

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())

points_model = ["396", "391", "386", "381", "376", "371", "366", "361", "356", "351",
                    "346", "341", "336", "331", "326", "321", "316", "311", "306", "301",
                    "296", "291", "286", "281", "276", "271", "266", "261", "256", "251",
                    "246", "241", "236", "231", "226", "221", "216", "211", "206", "201",
                    "196", "191", "186", "181", "176", "171", "166", "161", "156", "151",
                    "146", "141", "136", "131", "126", "121", "116", "111", "106", "101",
                    ]

points_summary = dict.fromkeys(points_model, 0)

@dp.message_handler(commands=['help', 'start'])
async def process_help_command(message: types.Message):
    current_datetime = datetime.now()
    URL_SOURCE = 'http://library.grsmu.by/priem/zaiv3D.html'

    r = requests.get(URL_SOURCE)
    r.encoding = 'utf-8'

    print("Connection success!")

    soup = bs(r.text, "html.parser")

    actual_time = soup.select_one(f'b:nth-of-type(1)').text

    actual_timeday = ''

    if (current_datetime.hour >= 8) and (current_datetime.hour <= 11):
        actual_timeday = f"Доброе утро! ☀\n\n*Данные актуальны на {actual_time}*"
    elif (current_datetime.hour >= 11) and (current_datetime.hour <= 16):
        actual_timeday = f"Добрый день! 🌴\n\n*Данные актуальны на {actual_time}*"
    elif (current_datetime.hour >= 16) and (current_datetime.hour <= 19):
        actual_timeday = f"Добрый вечер! 🌓\n\n*Данные актуальны на {actual_time}*"
    elif (current_datetime.hour >= 20) or (current_datetime.hour <= 7):
        actual_timeday = f"Доброй ночи! 🌛 \n\n*Данные актуальны на {actual_time}*"

    treat1 = soup.select_one("#container")
    treat2 = treat1.find("tr", class_="pink")

    summary_need = treat2.select_one('td:nth-of-type(2)').text
    summary_have = int(treat2.select_one('td:nth-of-type(3)').text)

    has_more_than_we = 0
    counter = 4
    points = 396
    s_points = 400
    raw_text = []
    client_text = []
    i = 0

    while i < 59:
        output = treat2.select_one(f'td:nth-of-type({str(counter)})').text
        output = output.replace(u'\xa0', u'0')
        points_summary[f"{points}"] = int(output)

        raw_text.append(f"{s_points}-{points} = {points_summary[f'{points}']} человек")

        if (points_summary[f'{points}'] == 0):
            pass
        else:
            client_text.append(f"{s_points}-{points} = {points_summary[f'{points}']} человек")

        s_points-=5
        points-=5
        i+=1
        counter+=1

    i=0
    points = 396
    while i < 17:
        if (points_summary[f'{points}'] == 0):
            pass
        else:
            has_more_than_we += points_summary[f'{points}']

        s_points -= 5
        points -= 5
        i += 1
        counter += 1

    has_less_than_we = summary_have - has_more_than_we
    has_more_than_we = f"{has_more_than_we-1} человек имеют *больший* балл ( не включая Сашу )."
    has_less_than_we = f"{has_less_than_we} человек имеют *меньший* балл."

    telegram_output = actual_timeday + f"\n\nПлан приема: {summary_need}" + f"\nПодано: {summary_have}" + f"\n\n{has_more_than_we}" + f"\n{has_less_than_we}" + f"\n\nДанные из таблицы можно увидеть ниже:\n\n" + f'\n'.join(client_text)
    await bot.send_message(message.from_user.id, text=f"{telegram_output}",parse_mode="Markdown")

    # telegram_output_raw = actual_timeday + f'\n'.join(raw_text)
    # await bot.send_message(message.from_user.id, text=f"В 'сыром' виде: \n{telegram_output_raw}")

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
