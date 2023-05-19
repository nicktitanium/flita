import telebot
import config_tg
import sqlite3
from telebot import types
queue = 0
reg_flag = 0
cnt = 0
in_queue = 0
client = telebot.TeleBot(config_tg.token)
conn = sqlite3.connect('users.db', check_same_thread=False)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    userid INT PRIMARY KEY,
    fname TEXT,
    lname TEXT);
""")
conn.commit()
reg_flag = False
@client.message_handler(commands = ["start"])
def start(message):
    cur.execute("SELECT fname, lname FROM users WHERE userid = ?", (str(message.from_user.id),))
    result = cur.fetchone()
    if result != None:
        global name
        name = str(result[0] + ' ' + result[1])
        config_tg.list.update({str(message.from_user.id): 0})
        client.send_message(message.chat.id,
                            "Здравствуй, товарищ младший заводчанин " + name + "!"
                            )
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_add = types.KeyboardButton("Встать в очередь")
        item_del = types.KeyboardButton("Отозвать заявку")
        markup_reply.add(item_add, item_del)
        client.send_message(message.chat.id, "Выберите действие",
                            reply_markup = markup_reply
                            )
    else:
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_reg = types.KeyboardButton("Зарегистрироваться")
        markup_reply.add(item_reg)
        client.send_message(message.chat.id, "Ваш идентификатор отсутствует в системе",
                            reply_markup=markup_reply
                            )

@client.message_handler(content_types=['text'])
def menu(message):
    global queue
    global cnt
    global in_queue
    user_id = str(message.from_user.id)
    config_tg.list.update({str(message.from_user.id): cnt})
    if message.text != 'Зарегистрироваться':
        cur.execute("SELECT fname, lname FROM users WHERE userid = ?", (str(message.from_user.id),))
        result = cur.fetchone()
        name = str(result[0] + ' ' + result[1])
        if message.text == 'Встать в очередь':
            if in_queue == 0:
                client.send_message("-1001964194217",
                                    "Новая заявка!\nИмя студента: " + name + "\nКоличество подходов: " + str(config_tg.list[user_id]))
                cnt += 1
                client.send_message(message.chat.id, "Ожидайте! Ваша позиция в очереди: " + str(queue))
                queue += 1
                in_queue = 1
            else:
                client.send_message(message.chat.id, "Вы не можете подать заявку, так как уже стоите в очереди.")
        elif message.text == 'Отозвать заявку':
            cur.execute("SELECT fname, lname FROM users WHERE userid = ?", (str(message.from_user.id),))
            result = cur.fetchone()
            name = str(result[0] + ' ' + result[1])
            if in_queue == 1:
                client.send_message("-1001964194217", "Заявка на имя " + name + " отозвана.")
                client.send_message(message.chat.id, "Ваша заявка отменена!")
                queue -= 1
                in_queue = 0
            else:
                client.send_message(message.chat.id, "Вы не можете отозвать заявку, так как не стоите в очереди.")
    elif message.text == 'Зарегистрироваться':
        global reg_flag
        reg_flag = 1
        mesg = client.send_message(message.chat.id, "Введи свои данные в формате: Фамилия Имя")
        client.register_next_step_handler(mesg, reg)
    else:
        client.send_message(message.chat.id, "Неизвестная команда! Повторите запрос.")
def reg(message):
    global reg_flag
    if reg_flag == 1:
        sqlite_insert_with_param = """INSERT OR IGNORE INTO users
                                      (userid, fname, lname)
                                      VALUES (?, ?, ?);"""
        last = message.text.split()[0]
        first = message.text.split()[1]
        data_tuple = (str(message.chat.id), first, last)
        cur.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_add = types.KeyboardButton("Встать в очередь")
        item_del = types.KeyboardButton("Отозвать заявку")
        markup_reply.add(item_add, item_del)
        client.send_message(message.chat.id, "Вы успешно зарегистрированы в системе. Для продолжения выберите нужную команду!",
                            reply_markup=markup_reply
                            )
client.infinity_polling()