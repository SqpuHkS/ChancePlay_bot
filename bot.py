import config
import telebot
import mysql

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def handle_start(message):
    temp = mysql.mysql_start_check(message)
    if temp == True:
        bot.send_message(message.chat.id,
                         'You are already registered, if you want to change your nickname press /change')
    else:
        msg = bot.send_message(message.chat.id, 'Write your nickname to start the game')
        bot.register_next_step_handler(msg, mysql.mysql_start_INSERT)

@bot.message_handler(commands=['change'])
def handle_change(message):
    msg = bot.send_message(message.chat.id, 'Write your new nickname')
    bot.register_next_step_handler(msg, next_step_change)

# Сделать реализацию команды имейл чтоб хранилась в базе и дать за это 50 коинов
# @bot.message_handler(commands=['email'])
# def handle_start(message):
#     temp = mysql.mysql_start_check(message)
#     if temp == True:
#         bot.send_message(message.chat.id,
#                          'You are already registered, if you want to change your nickname press /change')
#     else:
#         msg = bot.send_message(message.chat.id, 'Write your nickname to start the game')
#         bot.register_next_step_handler(msg, mysql.mysql_start_INSERT)

#Сделать реализацию ежедневого бонуса как колесо дает от 1 до 10 коинов
#Сделать реализацию таблицы, у кого больше 500 коинов те попадают в таблицу ... продолжение в заметках на телефоне

#ниже хрень нужна чтоб удалять потом сообщения бота ставок которые уже прошли, дату удаления ставить на начало матча, чтобы не ставили во время матча
#bot.delete_message(message.chat.id, message.message_id)





def next_step_change(message):
    temp = mysql.mysql_change_check(message)
    if temp == True:
        bot.send_message(message.chat.id,
                         'It\'s your nickname yet, if you want to change your nickname press /change')
    else:
        mysql.mysql_change_UPDATE(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)