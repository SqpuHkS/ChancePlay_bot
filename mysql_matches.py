from config import get_connection

#Все функции нужные для парсинга начинаются с 'parsing_'
#Все функции нужные для работы с ботом начинаются с 'mysql_'

#В качестве аргументов функции используем все данные требуемые
#для заполнения таблицы, и инициализируем начальные две ставки
def parsing_insert_data(home_team, guest_team, date, time, home_score, guest_score,status):
    connection = get_connection()
    if home_score == "" and guest_score == "":
        home_score, guest_score = 0,0
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO matches(home_team,
             guest_team,
              match_date,
               match_time,
                home_team_score,
                 guest_team_score,
                 match_status)
             VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cursor.execute(sql, (home_team, guest_team,date,time,home_score,guest_score, status))
        connection.commit()
    finally:
        connection.close()

#Функция для проверки существования опеределенных данных в таблице
def parsing_check_data(home_team, guest_team, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT * 
            FROM matches 
            WHERE home_team = "{}" 
            AND guest_team = "{}" 
            AND match_date = "{}"
            '''.format(home_team, guest_team, date)
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
            match_status = "{}"
            WHERE match_date = "{}"
            AND home_team = "{}"
            '''.format(home_score, guest_score, status, date, home_team)
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()


def mysql_select_home_teams(date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT home_team
                    FROM matches
                    WHERE match_date = "{}" AND
                    match_status = "{}"
                    '''.format(date, 1)
            return cursor.execute(sql)
    finally:
        connection.commit()
        connection.close()


def mysql_get_teams(data, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            foobar = []
            sql = '''SELECT {}
                    FROM matches
                    WHERE match_date = "{}" AND 
                    match_status = "{}"
                    '''.format(data, date, 1)
            cursor.execute(sql)
            for row in cursor:
                foobar.append(row[data])
            return foobar
    finally:
        connection.commit()
        connection.close()

#получает главное айди матча
def mysql_get_match_id(home_team, guest_team, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT match_id
                    FROM matches
                    WHERE home_team = "{}" AND 
                    guest_team = "{}" AND
                    match_date = "{}"
                    '''.format(home_team, guest_team, date)
            cursor.execute(sql)
            for row in cursor:
                return row["match_id"]
    finally:
        connection.commit()
        connection.close()

def mysql_get_status(match_id, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT match_status
                            FROM matches
                            WHERE match_id = {} AND 
                            match_date = "{}"
                            '''.format(match_id, date)
            cursor.execute(sql)
            for row in cursor:
                return row["match_status"]
    finally:
        connection.commit()
        connection.close()

def mysql_update_result():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE matches
                    SET matches.match_result = CASE
                        WHEN matches.home_team_score > matches.guest_team_score 
                            THEN 1
                        WHEN matches.home_team_score < matches.guest_team_score
                            THEN 2
                        WHEN matches.home_team_score = matches.guest_team_score
                            THEN 3
                        ELSE match_result
                        END
                    WHERE match_status = 2
                    AND match_result = 4;
                '''
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()