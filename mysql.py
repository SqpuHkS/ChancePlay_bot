import pymysql.cursors
from config import get_connection
import telebot
from bot import bot
from datetime import date

#Все функции нужные для парсинга начинаются с 'parsing_'
#Все функции нужные для работы с ботом начинаются с 'mysql_'

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

#В качестве аргументов функции используем все данные требуемые
#для заполнения таблицы, далее используя запрос вставляем новые даные в таблицу
def parsing_insert_data(home_team, guest_team, date, time, home_score, guest_score,status):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO matches(home_team,
             guest_team,
              match_date,
               match_time,
                home_team_score,
                 guest_team_score,
                 is_end)
             VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (home_team, guest_team,date,time,home_score,guest_score, status))
        connection.commit()
    finally:
        connection.close()

#Функция для проверки существования опеределенных данных в таблице
def parsing_check_data(home_team, guest_team, time):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT * 
            FROM matches 
            WHERE home_team = "{}" 
            AND guest_team = "{}" 
            AND match_time = "{}"
            '''.format(home_team, guest_team, time)
            if cursor.execute(sql)==0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()

#Функция для обновления данных (счета, статуса игры)
def parsing_update_data(home_score, guest_score, status, date, home_team):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE matches
            SET home_team_score = {},
            guest_team_score = {},
            is_end = "{}"
            WHERE match_date = "{}"
            AND home_team = "{}"
            '''.format(home_score, guest_score, status, date, home_team)
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

def mysql_select_home_teams():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT home_team
                    FROM matches
                    WHERE match_date = '{}'
                    '''.format(date.today())
            return cursor.execute(sql)
    finally:
        connection.commit()
        connection.close()


def mysql_get_teams(data):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            foobar = []
            sql = '''SELECT {}
                    FROM matches
                    WHERE match_date = '{}'
                    '''.format(data, date.today())
            cursor.execute(sql)
            for row in cursor:
                foobar.append(row[data])
            return foobar
    finally:
        connection.commit()
        connection.close()
