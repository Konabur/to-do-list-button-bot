import logging
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.utils.callback_data import CallbackData
import os, asyncio, traceback, json
import requests

# Объект бота
bot = Bot(token=os.getenv('TOKEN'))
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

task_cb = CallbackData('task', 'id', 'json')  # task:<id>:<json>
    
def get_task_keyboard(tasks):
    task_json = json.dumps(tasks)
    keyboard = types.InlineKeyboardMarkup()
    for i, task in enumerate(tasks):
        button = types.InlineKeyboardButton('❌✅'*task['done']+' %d. '%i+task['text'], callback_data=task_cb.new(id=i, json=task_json))
        keyboard.add(button)
    return keyboard
                                            
    
@dp.callback_query_handler(task_cb.filter())
async def task_modifier(query: types.CallbackQuery, callback_data: dict):
    tasks = json.loads(callback_data['json'])
    tasks[int(callback_data['id'])]['done'] = 1 - tasks[int(callback_data['id'])]['done']
    await query.message.edit_reply_markup(get_task_keyboard(tasks))
           
    
@dp.message_handler(filters.CommandStart())
async def start(message: types.Message) -> None:
    await message.answer('/start')
        
@dp.message_handler(filters.ChatTypeFilter('private'), content_types=['text'])
async def message_(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    tasks = []
    for line in message.text.split('\n'):
         tasks.append({'done': 0, 'text': line})
    await message.reply('План:', reply_markup=get_task_keyboard(tasks))


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
