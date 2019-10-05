import pymysql.cursors
from config import get_connection
import telebot
from datetime import date

#Все функции нужные для парсинга начинаются с 'parsing_'
#Все функции нужные для работы с ботом начинаются с 'mysql_'

#В качестве аргументов функции используем все данные требуемые
#для заполнения таблицы, и инициализируем начальные две ставки
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
                    WHERE match_date = '{}' AND
                    is_end = '{}'
                    '''.format(date.today(), 'WB')
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
                    WHERE match_date = '{}' AND 
                    is_end = '{}'
                    '''.format(data, date.today(), 'WB')
            cursor.execute(sql)
            for row in cursor:
                foobar.append(row[data])
            return foobar
    finally:
        connection.commit()
        connection.close()

#получает главное айди матча
def mysql_get_main_id(home_team, guest_team):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT main_id
                            FROM matches
                            WHERE home_team = '{}' AND 
                            guest_team = '{}' AND
                            match_date = '{}'
                            '''.format(home_team, guest_team, date.today())
            cursor.execute(sql)
            for row in cursor:
                return row['main_id']
    finally:
        connection.commit()
        connection.close()
