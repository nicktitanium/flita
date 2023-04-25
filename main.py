import telebot
import config_tg
from telebot import types

client = telebot.TeleBot(config_tg.token)

times = 0

@client.message_handler(commands = ["start"])
def start(message):
    user_id = str(message.from_user.id)
    if user_id in config_tg.names:
        client.send_message(message.chat.id,
                            "Здравствуй, товарищ младший заводчанин " + config_tg.names[user_id] + "!"
                            )
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_add = types.KeyboardButton("Встать в очередь")
        item_del = types.KeyboardButton("Отозвать заявку")
        markup_reply.add(item_add, item_del)
        client.send_message(message.chat.id, "Выберите действие",
                            reply_markup = markup_reply
                            )
    else:
        client.send_message(message.chat.id, "Ваш идентификатор отсутствует в системе")
@client.message_handler(content_types=['text'])
def menu(message):
    user_id = str(message.from_user.id)
    if message.text == 'Встать в очередь':
        client.send_message("-1001964194217",
                            "Новая заявка!\nИмя студента: " + config_tg.names[user_id] + "\nКоличество подходов: " + str(config_tg.times[user_id]))
        config_tg.times[user_id] += 1
        client.send_message(message.chat.id, "Ожидайте: ваша позиция в очереди: " + str(config_tg.queue))
    elif message.text == 'Отозвать заявку':
        client.send_message("-1001964194217", "Заявка на имя " + config_tg.names[user_id] + " отозвана.")
        client.send_message(message.chat.id, "Ваша заявка отменена!")
        config_tg.times[user_id] -= 1
    else:
        client.send_message(message.chat.id, "Неизвестная команда. Повторите запрос.")
client.infinity_polling()

