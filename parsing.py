from bs4 import BeautifulSoup
import requests
from config import MATCH_URL
import datetime
import mysql

#Получаем данные (статус игры, дату, время)
def get_data():
    time_info = requests.get(MATCH_URL, timeout=5)
    page_content = BeautifulSoup(time_info.content, 'html.parser')
    content = []
    for i in page_content.find_all(class_="match-row__status"):
        content.append(i.text.strip())
    return content


def get_home_teams():
    matches_info = requests.get(MATCH_URL, timeout = 5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='match-row__team-home'):
        content.append(i.text.strip())
    return content


def get_guest_teams():
    matches_info = requests.get(MATCH_URL, timeout=5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='match-row__team-away'):
        content.append(i.text.strip())
    return content


def get_score():
    matches_info = requests.get(MATCH_URL, timeout=5)
    matches_content = BeautifulSoup(matches_info.content, 'html.parser')
    content = []
    for i in matches_content.find_all(class_='match-row__goals'):
        content.append(i.text.strip())
    return content

def get_date():
    return datetime.date.today()

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


#получаем статус игры
def get_status():
    foo, bar = get_data(), []
    for i in foo:
        if i[:2] == 'FT':
            bar.append('FT')
        elif  check_time_for_status(i) == True:
            bar.append('FT')
        else:
            bar.append('WB')
    return bar

#проходит по сайту, ищет новые матчи и добавляет если такого не существует в БД
def insert_new_matches():
    home, guest, time, score, date, status = get_home_teams(), get_guest_teams(), get_time(), get_score(), get_date(), get_status()
    temp0, temp1 = -2, -1
    for i in range(len(home)):
        if mysql.parsing_check_data(home[i], guest[i], time[i]) == False:
            mysql.parsing_insert_data(home[i], guest[i], date, time[i], score[temp0+2], score[temp1+2], status[i])
        temp0 += 2
        temp1 += 2

#сделать функцию которая обновляет информацию в БД
def update_matches():
    score, status, home_team = get_score(), get_status(), get_home_teams()
    temp0, temp1 = -2, -1
    for i in range(len(status)):
        mysql.parsing_update_data(score[temp0+2], score[temp1+2], status[i], datetime.date.today(), home_team[i])
        temp0 += 2
        temp1 += 2

update_matches()