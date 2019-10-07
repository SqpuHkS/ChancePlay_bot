import pymysql.cursors
from config import get_connection
from datetime import date

def mysql_insert_bets(telegram_id, match_id, result, coefficient, tokens, status):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO bets(
            telegram_id,
            match_id,
            match_result,
            coefficient,
            tokens,
            status,
            bet_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            '''
            cursor.execute(sql, (telegram_id, match_id, result, coefficient, tokens, status, date.today()))
        connection.commit()
    finally:
        connection.close()

def mysql_get_tokens(match_id, match_result):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            temp = 0
            sql = '''SELECT {}
                        FROM bets
                        WHERE bet_date = '{}' AND 
                        match_id = '{}' AND 
                        match_result = {}
                        '''.format('tokens', date.today(), match_id, match_result)
            cursor.execute(sql)
            for row in cursor:
                temp += row['tokens']
            return temp
    finally:
        connection.commit()
        connection.close()

def mysql_insert_initial_bets(match_id, result, time):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO bets(
                telegram_id,
                match_id,
                match_result,
                coefficient,
                tokens,
                status,
                bet_date,
                match_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                '''
            cursor.execute(sql, (331328422, match_id, result, 1.5, 50, 2, date.today(), time))
        connection.commit()
    finally:
        connection.close()

def mysql_check_initial_bets(match_id, match_result):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT *
                FROM bets
                WHERE telegram_id = {} AND 
                match_id = {} AND
                match_result = {} AND
                tokens = {} AND
                bet_date = '{}'
                                '''.format(331328422, match_id, match_result, 50, date.today())
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()