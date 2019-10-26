from bs4 import BeautifulSoup
from config import MATCH_URL
from threading import Thread
import requests
import datetime
import mysql_matches
import mysql_bets
import time
import pytz




#Получаем данные с сайта в виде(статус игры, дата, время)
def get_data():
    matches_info = requests.get(MATCH_URL, timeout = 5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='football-match__status'):
       content.append(i.text.strip())
    return content

#получаем с сайта все команды которые будут играть сегодня дома
def get_home_teams():
    matches_info = requests.get(MATCH_URL, timeout = 5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    temp = 0
    for i in matches_content.find_all(class_='football-team__name team-name'):
        if temp % 2 == 0:
            content.append(i.text.strip())
        temp+=1
    return content


#получаем с сайта все команды которые будут играть сегодня в гостях
def get_guest_teams():
    matches_info = requests.get(MATCH_URL, timeout = 5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    temp = 1
    for i in matches_content.find_all(class_='football-team__name team-name'):
        if temp % 2 == 0:
            content.append(i.text.strip())
        temp+=1
    return content


#Получаем с сайта все забитые голы всех игр сегодня
def get_score():
    matches_info = requests.get(MATCH_URL, timeout=5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='football-team__score'):
        if i.text.strip() == '':
            content.append(0)
        else:
            content.append(i.text.strip())
    return content


#Возвращает актуальную дату на данный момент
def get_date():
    london_zone = pytz.timezone('Europe/London')
    return datetime.datetime.now(london_zone).strftime('%Y-%m-%d')


#Так как время на сайте на 2 часа меньше нашего, то прибавляем эти 2 часа и получаем
#Актуальное время игры по часовому поясу Украины
def get_time():
    foo, bar = get_data(), []
    for i in foo:
        if len(i) == 5 and i[2] == ':':
            temp = int(i[:2])
            bar.append(str(temp)+str(i)[2:])
        else:
            bar.append('STATUS')
    return bar



#получаем статус игры (FT - закончена, WB - предстоит, ST - началась но не закончилась)
#так же добавил проверку на случай если сайт по каким-то причинам не добавил
#в ячейку статуса игры ее конец (при помощи функции проверяю не прошло ли уже 2 часа после игры)
def get_status():
    foo, bar = get_data(), []
    for i in foo:
        if i == 'FT':
            bar.append('2')
        elif i == '1st' or i == '2nd' or i == 'HT':
            bar.append('3')
        elif len(i) == 5 and i[2] == ':':
            bar.append('1')
        else:
            bar.append('2')
    return bar

#инициализирую двумя ставками каждый из матчей, чтобы можно было отображать сразу коэффициент
def initial_bets(home_team, guest_team, date, i):
    match_id = mysql_matches.mysql_get_match_id(home_team[i], guest_team[i], date)
    if match_id == None:
        return None
    if mysql_bets.mysql_check_initial_bets(match_id, 1, date) == False and mysql_bets.mysql_check_initial_bets(match_id, 2, date) == False:
        mysql_bets.mysql_insert_initial_bets(match_id, 1, date)
        mysql_bets.mysql_insert_initial_bets(match_id, 2, date)

#проходит по сайту, ищет новые матчи и добавляет если такого не существует в БД
#функция нужна буквально раз в день либо каждый час для профилактики
def insert_new_matches():
    while True:
        home, guest, time0, \
        score, date, status = get_home_teams(), get_guest_teams(), get_time(), \
                            get_score(), get_date(), get_status()

        #начинаем с отрицательных и прибавляем каждую итерацию +2,
        #чтобы не попадало на те же цифры
        #к примеру -2+2 = 0, -1+2 = 1
        #след. итерация 0+2 = 2, 1+2 = 3 и т.д.
        temp0, temp1 = -2, -1
        for i in range(len(home)):
            #проверяю существуют ли уже такие данные в таблице
            if mysql_matches.parsing_check_data(home[i], guest[i], date) == False and len(time0[i]) == 5 and time0[i][2] == ':':
                mysql_matches.parsing_insert_data(home[i], guest[i], date, time0[i], score[temp0+2], score[temp1+2], status[i])
            if len(time0[i]) == 5 and time0[i][2] == ':':
                initial_bets(home, guest, date, i)
            temp0 += 2
            temp1 += 2
        print('insert')
        time.sleep(120)


#Обновляет информацию (счет команд, статус игр)
def update_matches_and_bets():
    while True:
        score, status, home_team = get_score(), get_status(), get_home_teams()
        temp0, temp1 = -2, -1
        for i in range(len(status)):
            mysql_matches.parsing_update_data(score[temp0+2], score[temp1+2], status[i], get_date(), home_team[i])
            temp0 += 2
            temp1 += 2
        mysql_bets.mysql_bets_update_match_status()
        mysql_matches.mysql_update_result()
        mysql_bets.mysql_update_result_and_pay_money()
        print('update')
        time.sleep(60)




if __name__ == "__main__":
    t1 = Thread(target=insert_new_matches)
    t2 = Thread(target=update_matches_and_bets)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass

