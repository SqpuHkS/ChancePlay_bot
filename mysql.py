import pymysql.cursors
from config import get_connection
import telebot
from bot import bot

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

def mysql_start_check(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM clients WHERE telegram_id = {}'.format(message.chat.id)
            if(cursor.execute(sql) == 0):
                return False
            else:
                return True
    finally:
        connection.close()

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

def mysql_change_check(message):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM clients WHERE telegram_id = {} AND nickname = "{}"'.format(message.chat.id, message.text)
            if(cursor.execute(sql) == 0):
                return False
            else:
                return True
    finally:
        connection.close()

#нужно сделать входящие данные которые принимаются как аргумент готовыми под типы данных в БД
#при чем данные должны быть в виде одного запроса, не все сразу
def parsing_add_teams(text_content):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = 'INSERT INTO matches(first_team_name, second_team_name, match_date) VALUES (%s, %s, %s)'
            cursor.execute(sql, (text_content[0], text_content[1], text_content[2]))
        connection.commit()
    finally:
        connection.close()