import telebot
from telebot import types

def start(data):

    token = "6613628769:AAEp3TsBsgCLKpFvAJVoPrxl3nXZhhwtGz4"
    bot=telebot.TeleBot(token)
    
    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, "Пропиши /button")
        
    @bot.message_handler(commands=['button'])
    def button_message(message):
        markup =types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1=types.KeyboardButton("🐟🐟🐟   ПРОВЕРИТЬ   🐟🐟🐟")
        markup.add(item1)
        
    @bot.message_handler(content_types='text')
    def message_reply(message):
        if message.text=="Проверить":
            messageText = f"Дней пройдено: {data['dayCount']}\nСделано забросов: {data['hookCount']}\nРыб поймано: {data['fishCount']}\nМусора поймано: {data['trashCount']}\nУровней получено: {data['levelupCount']}"
            bot.send_message(message.chat.id, messageText)
    						    
    bot.infinity_polling()

