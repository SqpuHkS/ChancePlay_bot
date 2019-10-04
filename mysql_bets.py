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

def mysql_get_tokens(match_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            temp = 0
            sql = '''SELECT {}
                        FROM bets
                        WHERE bet_date = '{}',
                        match_id = '{}'
                        '''.format('tokens', date.today(), match_id)
            cursor.execute(sql)
            for row in cursor:
                temp += row['tokens']
                print(temp)
            return temp
    finally:
        connection.commit()
        connection.close()

def mysql_insert_initial_bets(match_id, result):
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
            cursor.execute(sql, (331328422, match_id, result, 1.5, 50, 2, date.today()))
        connection.commit()
    finally:
        connection.close()

def mysql_check_initial_bets(match_id, match_result):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            print(match_id, match_result)
            sql = '''SELECT *
                FROM bets
                WHERE telegram_id = {} AND 
                match_id = {} AND
                match_result = {} AND
                coefficient = {} AND
                tokens = {} AND
                bet_date = '{}'
                                '''.format(331328422, match_id, match_result, 1.5, 50, date.today())
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()