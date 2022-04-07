import logging
from aiogram import Bot, Dispatcher, executor, types, filters
import os, asyncio, traceback
import requests

# Объект бота
bot = Bot(token=os.getenv('TOKEN'))
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

task_cb = CallbackData('task', 'id', 'json')  # task:<id>:<json>


@dp.message_handler(commands=['locate_me'])
async def cmd_locate_me(message: types.Message):
    reply = "Click on the the button below to share your location"
    keyboard = types.ReplyKeyboardMarkup()
    button = types.KeyboardButton("Share Position", request_location=True)
    keyboard.add(button)
    await message.answer(reply, reply_markup=keyboard)
    
@dp.message_handler(commands=['show'])
async def cmd_show(message: types.Message):
    staticmap(message.get_args())
    with open('temp.jp

@dp.message_handler(filters.CommandStart())
async def start(message: types.Message) -> None:
    message.answer('/start')
        
@dp.message_handler(filters.ChatType('private'), content_types=['text']))
async def message_(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    tasks = []
    for line in message.text.split('\n'):
         tasks.append({'done': 0, 'text': line})
    for task in enumerate(tasks):
        button = types.InlineKeyboardButton(, callback_data=task_cb.new(id=i, json=json(tasks))

        keyboard.add(button)
    await message.reply(text)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
