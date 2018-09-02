# -*- encoding: utf-8 -*-

from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import multiprocessing as mp
import os
import time
from datetime import datetime
import urllib3
urllib3.disable_warnings()
http = urllib3.PoolManager()



# Возвращает страницу и кол-во хозяев, если их меньше 2 и тачка не в розыске, и без штрафов.
def parse_hosts_count(page_url):
    # Get from the queue
    # And process it
    # TODO increase parsing speed
    page = urlopen(page_url)
    #page = requests.get(page_url)
    #print(page)
    soup = BeautifulSoup(page, 'html.parser')
    #soup = BeautifulSoup(page, 'lxml')


    # Парисм по тегу div'a
    hosts_field = soup.find_all(class_="b-media-cont b-media-cont_no-clear b-media-cont_bg_gray b-media-cont_modify_md b-random-group b-random-group_margin_b-size-xss")
    if len(hosts_field) == 0:
        return

    # Если тег есть, у нас список из одного элемента. Если лист пустой - просто pass с IndexError.
    # И по результату обрабатываем следующие теги, внутри него. Они называются одинакого, но у них есть определенный порядок всегда, в нем и отлавливаю.
    # По сути, если имя останется, но порядок изменится, работать перестанет. Но пока работает)
    criminal_search = hosts_field[0].find_all("div", {"class": "b-flex__item"})[3].text.strip()
    restricts = hosts_field[0].find_all("div", {"class": "b-flex__item"})[5].text.strip()
    hosts_count = hosts_field[0].find_all("div", {"class": "b-flex__item"})[1].text

    if criminal_search == "нет" and restricts == "нет" and int(hosts_count) <= 2:
         print("{} Хозяев: {}".format(page_url, hosts_count))



# Получаем список урлов со всех страниц по запросу с дрома.
def get_url_list(queue):

    page_number = 1
    #url_list = []
    url_count = 0

    while True:
        # Самый простой get query, пока не раскидал параметры запроса по переменным. Ну не суть.
        # По страницам бегаем просто подставляя номер новой, пока что то отдается.
        # Т.е. может открыться хоть 100500 страница, ошибки не будет, просто она будет без нужного контента.
        query = "https://kemerovo.drom.ru/auto/page{}/?distance=100&minprice=220000&maxprice=320000&minyear=2005&transmission=2&privod=1&ph=1&inomarka=1&order=price&order_d=desc&w=2&unsold=1&go_search=2".format(page_number)
        response = requests.get(query)
        soup = BeautifulSoup(response.text, 'html.parser')
        findings = soup.find_all(class_="b-media-cont b-media-cont_modifyMobile_sm")

        # Если пусто, значит наши страницы кончились.
        if len(findings) == 0:
            break

        for a in findings[0].find_all('a', href=True):
            #url_list.append(a['href'])
            #print("push {} to the queue".format(a['href']))
            queue.put(a['href'])
            url_count += 1

        page_number += 1


    return url_count


def reader(queue):
    while True:
        #print("get from the queue")
        page_url = queue.get()         # Read from the queue and do nothing

        if page_url is None:
            #print("TASKS ARE DONE,EXITING")
            break
        else:
            parse_hosts_count(page_url)


# Просто бегаем по урлам и выводим их.
def main():
    #get_url_list()

    num_workers = mp.cpu_count()
    print(num_workers)

    t = datetime.now()
    print(t)

    pqueue = mp.Queue()

    processes = [mp.Process(target=reader, args=(pqueue,)) for i in range(mp.cpu_count() + 2)]

    for proc in processes:
        proc.daemon = True
        proc.start()

    url_count = get_url_list(pqueue)

    for i in range(len(processes)):
        pqueue.put(None)

    for proc in processes:
        proc.join()

    print("Всего по данному фильтру было найдено найдено {} объявлений".format(url_count))
    print(datetime.now() - t)




if __name__ == '__main__':
    main()


# https://www.ellicium.com/python-multiprocessing-pool-process/
