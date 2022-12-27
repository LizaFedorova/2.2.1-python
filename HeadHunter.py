from typing import List, Dict
import pandas as pd
import requests
import concurrent.futures

class ProcessVacancies:
    """
    Класс для обработки и получения вакансий

    :param url: Адрес сайта
    :type url: str
    """
    def __init__(self, url: str):
        """
        :param url: Адрес сайта
        :type url: str
        """
        self.url = url

    def get_vacancies(self, params: dict) -> (List[Dict[str, str]] or List[Dict[Dict[str, str], str]]):
        """
        Получение вакансий по входным параметрам

        :param params: Параметры отбора
        :type params: dict

        :return: Набор вакансий
        :rtype: (List[Dict[str, str]] or List[Dict[Dict[str, str], str]])
        """
        return requests.get(self.url, params).json()['items']

    @staticmethod
    def process_vacancies(vacancies) -> list:
        """
        Обработка вакансий в формате словаря к формату списка

        :param vacancies: Набор вакансий
        :type vacancies: list

        :return: Набор вакансий
        :rtype: list
        """
        if len(vacancies) == 0:
            return []

        return [[vacancy['name'], vacancy['area']['name'], vacancy['salary']['from'], vacancy['salary']['to'],
                 vacancy['salary']['currency'], vacancy['published_at']] for vacancy in vacancies if vacancy['salary']]


if __name__ == '__main__':
    num_pages = 20
    first_part_params = [dict(specialization=1, date_from="2022-12-05T00:00:00", date_to="2022-12-05T12:00:00",
                              per_page=100, page=i) for i in range(num_pages)]

    second_part_params = [dict(specialization=1, date_from="2022-12-05T00:12:00", date_to="2022-12-06T00:00:00",
                               per_page=100, page=i) for i in range(num_pages)]

    process = ProcessVacancies('https://api.hh.ru/vacancies')

    with concurrent.futures.ProcessPoolExecutor() as executor:
        res = list(executor.map(process.get_vacancies, first_part_params + second_part_params))
        r = list(executor.map(process.process_vacancies, res))

    res = pd.concat([pd.DataFrame(el, columns=['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']) for el in r])
    res.to_csv("vacancies_hh.csv", index=False)
