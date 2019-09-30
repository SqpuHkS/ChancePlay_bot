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
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
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
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()

#нужно сделать входящие данные которые принимаются как аргумент готовыми под типы данных в БД
#при чем данные должны быть в виде одного запроса, не все сразу
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