from config import get_connection
from bot import bot

#Добавляет пользователя в базу данных
def mysql_start_INSERT(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO clients (telegram_id, nickname, tokens) VALUES (%s, %s, %s)"
            cursor.execute(sql, (message.chat.id, message.text, 100))
            bot.send_message(message.chat.id, 'Your account have been created, you have 100 tokens in your pocket')
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
            bot.send_message(message.chat.id, 'Changes saved')
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
                return row['tokens']
    finally:
        connection.commit()
        connection.close()