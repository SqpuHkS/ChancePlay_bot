import config
import telebot
import mysql_matches
import mysql_bets
import mysql_clients
import random
import string
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from parsing import get_date

#Сделать чтобы запрос отправился со статусом (WAIT) в ставку, а после того как пользователь ввел сумму ставки
#UPDATE ставку изменить сумму ставки и изменить статус ставки на (DONE)

bot = telebot.TeleBot(config.token)

def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def next_step_bet(message):
    try:
        if message.text.isdigit() and int(message.text) <= mysql_clients.mysql_get_tokens(message.from_user.id)\
                and int(message.text) > 0:
            if mysql_clients.mysql_user_tokens_minus_bet(message.from_user.id, message.text) == True:
                main_id = mysql_bets.mysql_get_main_id(message.from_user.id, get_date())
                mysql_bets.mysql_update_bets(main_id[-1], message.text)
                bot.send_message(message.chat.id, "Your bet has been processed")
        else:
            bot.send_message(message.chat.id, "Something is WrOnG!. \n\nTry it again /matches")
    except:
        bot.send_message(message.chat.id, "Something is WrOnG!. \n\nTry it again /matches")

def home_coef(home_bet_tokens, guest_bet_tokens):
    try:
        return round((home_bet_tokens+guest_bet_tokens)/home_bet_tokens, 2)
    except ZeroDivisionError:
        return 1.5

def guest_coef(home_bet_tokens, guest_bet_tokens):
    try:
        return round((home_bet_tokens+guest_bet_tokens)/guest_bet_tokens, 2)
    except ZeroDivisionError:
        return 1.5

def draw_coef(home_bet_tokens, guest_bet_tokens):
    try:
        if home_bet_tokens > guest_bet_tokens:
            return round(home_bet_tokens/guest_bet_tokens, 2)+0.5
        else:
            return round(guest_bet_tokens/home_bet_tokens, 2)+0.5
    except ZeroDivisionError:
        return 1.5

#added it
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    length, home_team, guest_team, id = mysql_matches.mysql_select_home_teams(get_date()), mysql_matches.mysql_get_teams('home_team', get_date()), \
                                        mysql_matches.mysql_get_teams('guest_team', get_date()), mysql_matches.mysql_get_teams('match_id', get_date())

    for i in range(length):
        markup.add(InlineKeyboardButton(home_team[i]+'  —  '+guest_team[i],
                                        callback_data='cb_match{}'.format(id[i])))
    return markup

#added it
#создает кнопки для ставок
def gen_bet(i, home_team_bet, guest_team_bet, draw_team_bet):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    home_team, guest_team, id = mysql_matches.mysql_get_teams('home_team', get_date()), \
                                        mysql_matches.mysql_get_teams('guest_team', get_date()), mysql_matches.mysql_get_teams('match_id', get_date())
    markup.add(InlineKeyboardButton(home_team[i] + '  ({})'.format(home_team_bet), callback_data='cb_home_team_{}'.format(id[i])),
                   InlineKeyboardButton(guest_team[i] + '  ({})'.format(guest_team_bet), callback_data='cb_guest_team_{}'.format(id[i])),
                    InlineKeyboardButton('Draw' + '  ({})'.format(draw_team_bet), callback_data='cb_draw_{}'.format(id[i])))
    return markup



#added it
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    length, home_team, guest_team, id, tokens = mysql_matches.mysql_select_home_teams(get_date()),\
                                                mysql_matches.mysql_get_teams('home_team', get_date()), \
                                                mysql_matches.mysql_get_teams('guest_team', get_date()),\
                                                mysql_matches.mysql_get_teams('match_id', get_date()),\
                                                mysql_clients.mysql_get_tokens(call.from_user.id),

    msg = "You have {} tokens. \n\nHow many tokens do you want to bet?".format(tokens)
    for i in range(length):
        home_bet_tokens, guest_bet_tokens, draw_bet_tokens = mysql_bets.mysql_get_tokens(id[i], 1, get_date()),\
                                                             mysql_bets.mysql_get_tokens(id[i], 2, get_date()),\
                                                             mysql_bets.mysql_get_tokens(id[i], 3, get_date())
        home_team_bet, guest_team_bet, draw_team_bet = home_coef(home_bet_tokens, guest_bet_tokens), \
                                                       guest_coef(home_bet_tokens, guest_bet_tokens), \
                                                       draw_coef(home_bet_tokens, guest_bet_tokens)
        if call.data == 'cb_match{}'.format(id[i]) and mysql_matches.mysql_get_status(id[i], get_date()) == 1:
            txt = 'Match coefficients: \t\n{home_team}  ({home_bet})\t\nDraw  ({draw})\t\n{guest_team}  ({guest_bet})\n'.format(home_team = home_team[i],
                                                                                                                   home_bet = home_team_bet,
                                                                                                                   draw = draw_team_bet,
                                                                                                                   guest_team = guest_team[i],
                                                                                                                   guest_bet = guest_team_bet)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   text=txt, reply_markup=gen_bet(i, home_team_bet, guest_team_bet, draw_team_bet))

        if call.data == 'cb_home_team_{}'.format(id[i]) and mysql_matches.mysql_get_status(id[i], get_date()) == 1:
            msg_edit = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)
            mysql_bets.mysql_insert_bets(call.from_user.id, id[i], 1, home_team_bet, -1, 1, 1, get_date())
            bot.register_next_step_handler(msg_edit, next_step_bet)

        if call.data == 'cb_guest_team_{}'.format(id[i]) and mysql_matches.mysql_get_status(id[i], get_date()) == 1:
            msg_edit = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)
            mysql_bets.mysql_insert_bets(call.from_user.id, id[i], 2, guest_team_bet, -1, 1, 1, get_date())
            bot.register_next_step_handler(msg_edit, next_step_bet)

        if call. data == 'cb_draw_{}'.format(id[i]) and mysql_matches.mysql_get_status(id[i], get_date()) == 1:
            msg_edit = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg)
            mysql_bets.mysql_insert_bets(call.from_user.id, id[i], 3, draw_team_bet, -1, 1, 1, get_date())
            bot.register_next_step_handler(msg_edit, next_step_bet)




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
    if mysql_matches.mysql_select_home_teams(get_date()) == 0:
        bot.send_message(message.chat.id, "Oops, no matches yet. ")
    else:
        bot.send_message(message.chat.id, "Today's matches:" , reply_markup=gen_markup())

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