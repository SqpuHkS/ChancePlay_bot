from config import get_connection
from bot import bot, id_generator

#Добавляет пользователя в базу данных
def mysql_start_INSERT(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            ref_code = id_generator()
            sql = 'INSERT INTO clients (telegram_id, nickname, tokens, promo_code) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (message.chat.id, message.text, 100, ref_code))
            bot.send_message(message.chat.id,
                '''Your account have been created, you have 100 tokens in your pocket\n
    Also your referral code is:  {}
    More information: /info'''.format(ref_code))
        connection.commit()
    finally:
        connection.close()

#Проверяет зарегистрирован ли пользователь уже в БД
def mysql_start_check(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM clients WHERE telegram_id = {}'.format(message.chat.id)
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()


#Изменение имени пользователя
def mysql_change_UPDATE(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'UPDATE clients SET nickname = "{}" WHERE telegram_id = {}'.format(message.text, message.chat.id)
            cursor.execute(sql)
            bot.send_message(message.chat.id, "Changes saved")
        connection.commit()
    finally:
        connection.close()

#Проверяет случайно не тот же никнейм что и нынешний вводит пользователь
def mysql_change_check(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM clients WHERE telegram_id = {} AND nickname = "{}"'.format(message.chat.id, message.text)
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()

def mysql_get_tokens(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT tokens
                    FROM clients
                    WHERE telegram_id = {}
                                '''.format(user_id)
            cursor.execute(sql)
            for row in cursor:
                return row["tokens"]
    finally:
        connection.commit()
        connection.close()

def mysql_user_tokens_minus_bet(user_id, bet):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE clients
            SET tokens = tokens - {}
            WHERE telegram_id = {}
                                '''.format(bet, user_id)
            cursor.execute(sql)
            return True
    except:
        return False
    finally:
        connection.commit()
        connection.close()

def pay_money():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE clients, bets
                    SET clients.tokens = clients.tokens + bets.tokens * bets.coefficient
                    WHERE clients.telegram_id = bets.telegram_id 
                    AND bets.match_status = 2
                    AND result_of_bet = 1
                                    '''
            cursor.execute(sql)
    finally:
        connection.commit()
        connection.close()