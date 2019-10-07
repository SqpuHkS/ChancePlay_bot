from bs4 import BeautifulSoup
import requests
from config import MATCH_URL
import datetime
import mysql_matches
import mysql_bets
import time
from threading import Thread




#Получаем данные с сайта в виде(статус игры, дата, время)
def get_data():
    time_info = requests.get(MATCH_URL, timeout=5)
    page_content = BeautifulSoup(time_info.content, 'html.parser')
    content = []
    for i in page_content.find_all(class_="match-row__status"):
        content.append(i.text.strip())
    return content

#получаем с сайта все команды которые будут играть сегодня дома
def get_home_teams():
    matches_info = requests.get(MATCH_URL, timeout = 5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='match-row__team-home'):
        content.append(i.text.strip())
    return content

#получаем с сайта все команды которые будут играть сегодня в гостях
def get_guest_teams():
    matches_info = requests.get(MATCH_URL, timeout=5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='match-row__team-away'):
        content.append(i.text.strip())
    return content

#Получаем с сайта все забитые голы всех игр сегодня
def get_score():
    matches_info = requests.get(MATCH_URL, timeout=5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='match-row__goals'):
        content.append(i.text.strip())
    return content

#Возвращает актуальную дату на данный момент
def get_date():
    return datetime.date.today()

#Так как время на сайте на 2 часа меньше нашего, то прибавляем эти 2 часа и получаем
#Актуальное время игры по часовому поясу Украины
def get_time():
    foo, bar = get_data(), []
    for i in foo:
        temp = i[-10:-5]
        i = int(temp[:2])+2
        bar.append(str(i)+str(temp[2:]))
    return bar


#Проверяем на всякий случай, если сайт ошибся и не выставил статус игры FT, увеличиваем время на 2 часа
#Чтоб стало по часовому поясу равно нашему времени и  еще на 2 чтоб игра точно закончилась
#И сверяем и предоставляем статус игры FT
def check_time_for_status(iterable):
    time_func, time_lib = get_time(), datetime.datetime.now().strftime('%H')
    if int(iterable[-10:-8])+4 < int(time_lib):
        return True
    else:
        return False


#получаем статус игры (FT - закончена, WB - предстоит, ST - началась но не закончилась)
#так же добавил проверку на случай если сайт по каким-то причинам не добавил
#в ячейку статуса игры ее конец (при помощи функции проверяю не прошло ли уже 2 часа после игры)
def get_status():
    foo, bar = get_data(), []
    for i in foo:
        temp = i[:2]
        if temp == 'FT':
            bar.append('FT')
        elif  check_time_for_status(i) == True:
            bar.append('FT')
        elif "'" in i[:4] or temp == 'HT':
            bar.append('ST')
        else:
            bar.append('WB')
    return bar

#инициализирую двумя ставками каждый из матчей, чтобы можно было отображать сразу коэффициент
def initial_bets(home_team, guest_team, get_time):
    for i in range(len(home_team)):
        main_id = mysql_matches.mysql_get_main_id(home_team[i], guest_team[i])
        if main_id == None:
            continue
        if mysql_bets.mysql_check_initial_bets(main_id, 1) == False and mysql_bets.mysql_check_initial_bets(main_id, 2) == False:
            mysql_bets.mysql_insert_initial_bets(main_id, 1, get_time[i])
            mysql_bets.mysql_insert_initial_bets(main_id, 2, get_time[i])

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
            if mysql_matches.parsing_check_data(home[i], guest[i], time0[i]) == False:
                mysql_matches.parsing_insert_data(home[i], guest[i], date, time0[i], score[temp0+2], score[temp1+2], status[i])
            temp0 += 2
            temp1 += 2
        initial_bets(home, guest, time0)
        print('insert')
        time.sleep(120)

#Обновляет информацию (счет команд, статус игр)
def update_matches():
    while True:
        score, status, home_team = get_score(), get_status(), get_home_teams()
        temp0, temp1 = -2, -1
        for i in range(len(status)):
            mysql_matches.parsing_update_data(score[temp0+2], score[temp1+2], status[i], datetime.date.today(), home_team[i])
            temp0 += 2
            temp1 += 2
        print('update')
        time.sleep(60)


if __name__ == "__main__":
    t1 = Thread(target=insert_new_matches)
    t2 = Thread(target=update_matches)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    while True:
        pass

