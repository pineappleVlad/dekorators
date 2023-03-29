import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import json
import datetime
import os

def logger(path):
    if os.path.exists(path):
        os.remove(path)
    def __logger(old_function):
        run_time = datetime.datetime.now()
        def new_function(*args, **kwargs):
            result = old_function(*args, **kwargs)
            result_string = f'Run time: {run_time}, Name: {old_function.__name__}, Args: {args}, Kwargs: {kwargs}, Result: {result} \n'
            with open(path, 'a', encoding="UTF-8") as file:
                file.write(result_string)
            return result
        return new_function
    return __logger


@logger('web_scrapping.log')
def get_headers():
    headers = Headers(browser="firefox", os='win')
    return headers.generate()

@logger('web_scrapping.log')
def hh_parsing_rubbles():
    HOST = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    response_vacancies = requests.get(HOST, headers=get_headers()).text
    soup = BeautifulSoup(response_vacancies, features='lxml')
    vacanсies_list = soup.find('main', class_='vacancy-serp-content')
    vacanсies = vacanсies_list.find_all('div', class_='serp-item')
    parsed = []
    for vacanсy in vacanсies:

        title = vacanсy.find('a', class_='serp-item__title')
        link = title['href']

        response = requests.get(link, headers=get_headers())
        vacanсy_article = BeautifulSoup(response.text, features='lxml')
        vacancy_description = vacanсy_article.find('div', {'data-qa': 'vacancy-description'}).text
        if ('django' in vacancy_description.lower()) or ('flask' in vacancy_description.lower()):
            fork = vacanсy.find('span', class_='bloko-header-section-3')
            if fork is not None:
                fork = fork.text.strip()
            else:
                fork = 'з/п не указана'
            company = vacanсy.find('a', class_='bloko-link bloko-link_kind-tertiary').text
            city = vacanсy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text
            item = {
                'Ссылка': link,
                'Вилка зп': fork,
                'Компания': company,
                'Город': city
            }
            parsed.append(item)
    return parsed

if __name__ == "__main__":
    parsed_rub = hh_parsing_rubbles()
    with open('vacancies.json', 'w', encoding='UTF-8') as file:
        json.dump(parsed_rub, file, indent=5, ensure_ascii=False)