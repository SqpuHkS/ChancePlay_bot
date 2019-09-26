from bs4 import BeautifulSoup
import requests
# print(text_content)
from config import URL


#
#РЕАЛИЗОВАТЬ ВСЕ НОРМАЛЬНО ЧЕРЕЗ ФУНКЦИИ БЕЗ ГЛОБАЛЬНЫХ ПЕРЕМЕННЫХ И Т.Д.
#
#ПОДГОТОВИТЬ ДАННЫЕ ДЛЯ ОТПРАВКИ В БАЗУ (ПРИВЕСТИ ИХ К НУЖНОМУ ТИПУ)

BASE_URL = URL

page_information = requests.get(BASE_URL, timeout = 5)
page_content = BeautifulSoup(page_information.content, 'html.parser')

text_content = []
# a=0
for i in page_content.find_all(class_="teams-container"):
    text_content.append(i.text)
    # text_content[a] = text_content[a].strip()
    # a+=1
print(text_content)

for i in page_content.find_all(class_="date ui-countdown"):
    print(i.text)
#