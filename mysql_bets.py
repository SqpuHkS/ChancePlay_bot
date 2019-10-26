from config import get_connection

def mysql_insert_bets(telegram_id, match_id, result, coefficient, tokens, match_status, bet_status, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO bets(
            telegram_id,
            match_id,
            match_bet_result,
            coefficient,
            tokens,
            match_status,
            bet_status,
            bet_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            '''
            cursor.execute(sql, (telegram_id, match_id, result, coefficient, tokens, match_status, bet_status, date))
        connection.commit()
    finally:
        connection.close()

def mysql_get_tokens(match_id, match_bet_result, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            temp = 0
            sql = '''SELECT {}
                        FROM bets
                        WHERE bet_date = "{}" AND 
                        match_id = "{}" AND 
                        match_bet_result = {} AND 
                        bet_status = {}
                        '''.format('tokens', date, match_id, match_bet_result, 2)
            cursor.execute(sql)
            for row in cursor:
                temp += row['tokens']
            return temp
    finally:
        connection.commit()
        connection.close()

def mysql_insert_initial_bets(match_id, result, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''INSERT INTO bets(
                telegram_id,
                match_id,
                match_bet_result,
                coefficient,
                tokens,
                match_status,
                bet_status,
                bet_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                '''
            cursor.execute(sql, (398000427, match_id, result, 1.5, 50, 1, 2, date))
        connection.commit()
    finally:
        connection.close()

def mysql_check_initial_bets(match_id, match_result, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT *
                FROM bets
                WHERE telegram_id = {} AND 
                match_id = {} AND
                match_bet_result = {} AND
                tokens = {} AND
                bet_date = "{}"
                                '''.format(398000427, match_id, match_result, 50, date)
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()

def mysql_get_main_id(telegram_id, date):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            temp = []
            sql = '''SELECT main_id
                            FROM bets
                            WHERE bet_date = "{}" AND 
                            telegram_id = "{}" AND 
                            tokens = {} AND
                            bet_status = {} AND 
                            match_status = {}
                            '''.format(date, telegram_id, -1, 1, 1)
            cursor.execute(sql)
            for row in cursor:
                temp.append(row["main_id"])
            return temp
    finally:
        connection.commit()
        connection.close()

def mysql_update_bets(main_id, tokens):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE bets
                SET tokens = {},
                bet_status = {}
                WHERE main_id = {}
                '''.format(tokens, 2, main_id)
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

def mysql_bets_update_match_status():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE bets, matches
                    SET bets.match_status = matches.match_status
                    WHERE bets.match_id = matches.match_id
                    AND bets.match_status != matches.match_status
                '''
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

def mysql_check_status_and_result():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''SELECT *
                    FROM bets
                    WHERE match_status = 2 
                    AND result_of_bet = 1
                    '''
            if cursor.execute(sql) == 0:
                return False
            else:
                return True
    finally:
        connection.commit()
        connection.close()

def mysql_update_result_and_pay_money():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = '''UPDATE bets, clients, matches
                    SET clients.tokens = CASE
                        WHEN bets.match_bet_result = matches.match_result
                            THEN clients.tokens + (bets.tokens * bets.coefficient)
                            ELSE clients.tokens
                        END, 
                    bets.result_of_bet = CASE
                        WHEN bets.match_bet_result = matches.match_result
                            THEN bets.result_of_bet = 2
                        WHEN bets.match_bet_result != matches.match_result
                            THEN bets.result_of_bet = 3
                            ELSE bets.result_of_bet
                        END
                    WHERE matches.match_status = 2
                    AND bets.result_of_bet = 1
                    AND bet_status = 2
                    '''
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()