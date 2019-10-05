import config
import telebot
import mysql_matches
import mysql_bets
import mysql_clients
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot(config.token)

def get_coefficient():
    id = mysql_matches.mysql_get_teams('main_id')
    for i in id:
        temp0 = mysql_bets.mysql_get_tokens(i)

#added it
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    length, home_team, guest_team, id, time = mysql_matches.mysql_select_home_teams(), mysql_matches.mysql_get_teams('home_team'), \
                                        mysql_matches.mysql_get_teams('guest_team'), mysql_matches.mysql_get_teams('main_id'), \
                                        mysql_matches.mysql_get_teams('match_time')
    for i in range(length):
        markup.add(InlineKeyboardButton(home_team[i]+' — '+str(time[i])[:-3]+' — '+guest_team[i], callback_data='cb_match{}'.format(id[i])))
    return markup

#added it
#создает кнопки для ставок
def gen_bet():
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    length, home_team, guest_team, id = mysql_matches.mysql_select_home_teams(), mysql_matches.mysql_get_teams('home_team'), \
                                        mysql_matches.mysql_get_teams('guest_team'), mysql_matches.mysql_get_teams('main_id')
    for i in range(length):
        markup.add(InlineKeyboardButton(home_team[i], callback_data='cb_home_team_{}'.format(id[i])),
                   InlineKeyboardButton(guest_team[i], callback_data='cb_guest_team_{}'.format(id[i])),
                    InlineKeyboardButton('Draw', callback_data='cb_draw_{}'.format(id[i])))
    return markup


#added it
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    length, home_team, guest_team, id = mysql_matches.mysql_select_home_teams(), mysql_matches.mysql_get_teams('home_team'), \
                                        mysql_matches.mysql_get_teams('guest_team'), mysql_matches.mysql_get_teams('main_id')
    for i in range(length):
        if call.data == 'cb_match{}'.format(id[i]):
            gen_bet()
            #формирую запрос, но жду следующего шага чтобы отправить запрос с количеством денег в ставке
            #сохраняю данные в состояние и после того как написал количество вызываю запрос INSERT данных в таблице бэт

@bot.message_handler(commands=['start'])
def handle_start(message):
    temp = mysql_clients.mysql_start_check(message)
    if temp == True:
        bot.send_message(message.chat.id,
                         'You are already registered, if you want to change your nickname press /change')
    else:
        msg = bot.send_message(message.chat.id, 'Write your nickname to start the game')
        bot.register_next_step_handler(msg, mysql_clients.mysql_start_INSERT)

@bot.message_handler(commands=['change'])
def handle_change(message):
    msg = bot.send_message(message.chat.id, 'Write your new nickname')
    bot.register_next_step_handler(msg, next_step_change)

# @bot.callback_query_handler(func=lambda call: True)
# def callback_query(call):
#     if call.data ==

@bot.message_handler(commands=['matches'])
def handle_matches(message):
    bot.send_message(message.chat.id, "Today's matches:", reply_markup=gen_markup())


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
#либо же можно использовать editMessageText, но про нее стопроцентно не знаю, надо узнать


# def next_first_step_bet(call):



def next_step_change(message):
    temp = mysql_clients.mysql_change_check(message)
    if temp == True:
        bot.send_message(message.chat.id,
                         'It\'s your nickname yet, if you want to change your nickname press /change')
    else:
        mysql_clients.mysql_change_UPDATE(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)