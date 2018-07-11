# -*- encoding: utf-8 -*-

from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

# Возвращает страницу и кол-во хозяев, если их меньше 2 и тачка не в розыске, и без штрафов.
def parse_hosts_count(page_url):
    page = urlopen(page_url)
    soup = BeautifulSoup(page, 'html.parser')

    hosts_field = soup.find_all(class_="b-media-cont b-media-cont_no-clear b-media-cont_bg_gray b-media-cont_modify_md b-random-group b-random-group_margin_b-size-xss")

    try:
        criminal_search = hosts_field[0].find_all("div", {"class":"b-flex__item"})[3].text.strip()
        restricts = hosts_field[0].find_all("div", {"class":"b-flex__item"})[5].text.strip()
        hosts_count = hosts_field[0].find_all("div", {"class":"b-flex__item"})[1].text

        if criminal_search == "нет" and restricts == "нет" and int(hosts_count) <= 2:
            print("{} Хозяев: {}".format(page_url, hosts_count))

    except IndexError:
        pass

# Получаем список урлов со всех страниц по запросу с дрома.
def get_url_list():

    page_number = 1
    url_list = []

    while True:
        query = "https://kemerovo.drom.ru/auto/page{}/?distance=100&minprice=250000&maxprice=320000&minyear=2005&transmission=2&privod=1&ph=1&inomarka=1&order=price&order_d=desc&w=2&unsold=1&go_search=2".format(page_number)
        response = requests.get(query)
        soup = BeautifulSoup(response.text, 'html.parser')
        findings = soup.find_all(class_="b-media-cont b-media-cont_modifyMobile_sm")

        if len(findings) == 0:
            break

        for a in findings[0].find_all('a', href=True):
            url_list.append(a['href'])

        page_number += 1

    return url_list


def main():
    url_list = get_url_list()
    print("Найдено {} объявлений".format(len(url_list)))

    for url in url_list:
        parse_hosts_count(url)



if __name__ == '__main__':
    main()
