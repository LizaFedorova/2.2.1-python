import pandas as pd
import requests
import xml.etree.ElementTree as ET

class ProcessCurrencies:
    """
    Работает с API ЦБ, позволяя получить историю курсов валют в формате CSV
    """
    def __init__(self, file_name: str) -> None:
        """
        Инициализирует объект класса, высчитывает даты самой старой и самой новой вакансии

        :param file_name: Имя файла с вакансиями
        :type file_name: str
        """
        self.df = pd.read_csv(file_name)
        self.min_date = self.df['published_at'].min()
        self.max_date = self.df['published_at'].max()
        self.currencies_to_convert = None
        self.currencies_data = None

    def get_currencies_to_convert(self, n=5000) -> list:
        """
        Выбирает только те валюты, которые встречаются в выборе более чем n раз

        :param n: Частотность
        :type n: int

        :return: Список валют
        :rtype: list
        """
        result = []
        currency_counts = self.df['salary_currency'].value_counts()
        for currency, count in currency_counts.items():
            print(currency, count)
            if count > n:
                result.append(currency)
        self.currencies_to_convert = result
        return result

    def get_row(self, month: str, year: str) -> list or None:
        """
        Формирует список с курсами валют за указанный месяц

        :param month: Месяц, по которому будет проходить запрос
        :type month: str

        :param year: Год, по которому будет проходить запрос
        :type year: str

        :return: Список с курсами валют
        :rtype: list or None
        """
        try:
            format_month = ('0' + str(month))[-2:]
            url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=02/{format_month}/{year}'
            res = requests.get(url)
            tree = ET.fromstring(res.content)
            row = [f'{year}-{format_month}']
            for value in self.currencies_to_convert:
                if value == 'RUR':
                    row.append(1)
                    continue
                found = False
                for valute in tree:
                    if valute[1].text == value:
                        row.append(round(float(valute[4].text.replace(',', '.')) / float(valute[2].text.replace(',', '.')), 6))
                        found = True
                        break
                if not found:
                    row.append(None)
            return row

        except Exception:
            return None

    def generate_currency(self, start_date: str, finish_date: str) -> None:
        """
        Создаёт CSV-файл с курсами валют за необходимый период

        :param start_date: Начало периода
        :type start_date: str

        :param finish_date: Конец периода
        :type finish_date: str
        """
        first_year = int(start_date[:4])
        first_month = int(start_date[5:7])
        last_year = int(finish_date[:4])
        last_month = int(finish_date[5:7])

        dataframe = pd.DataFrame(columns=['date'] + self.currencies_to_convert)
        for year in range(first_year, last_year + 1):
            for month in range(1, 13):
                if (year == first_year and month < first_month) or (year == last_year and month > last_month):
                    continue
                row = self.get_row(month, year)
                if row is None:
                    continue
                dataframe.loc[len(dataframe.index)] = row

        self.currencies_data = dataframe
        dataframe.to_csv('dataframe.csv')

class ProcessSalaries:
    def __init__(self, file_name: str) -> None:
        """
        Инициализирует объект ProcessSalaries

        :param file_name: Имя файла для обработки
        :type file_name: str
        """
        self.file_name = file_name
        self.currencies = pd.read_csv('dataframe.csv')
        self.available_currencies = list(self.currencies.keys()[2:])

    def process_salaries(self) -> None:
        """
        Обрабатывает зарплаты, переводя в рубли в соответствии с нужным курсом. Сохраняет в формате CSV
        """
        salaries = []
        to_delete = []
        df = pd.read_csv(self.file_name)

        for row in df.itertuples():
            salary_from = str(row[2])
            salary_to = str(row[3])

            if salary_from != 'nan' and salary_to != 'nan':
                salary = float(salary_from) + float(salary_to)

            elif salary_from != 'nan' and salary_to == 'nan':
                salary = float(salary_from)

            elif salary_from == 'nan' and salary_to != 'nan':
                salary = float(salary_to)

            else:
                to_delete.append(int(row[0]))
                continue

            if row[4] != 'RUR':
                date = row[6][:7]
                multiplier = self.currencies[self.currencies['date'] == date][row[4]].iat[0]
                salary *= multiplier

            if row[4] == 'nan' or row[4] not in self.available_currencies:
                to_delete.append(int(row[0]))
                continue

            salaries.append(salary)

        df.drop(labels=to_delete, axis=0, inplace=True)
        df.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        df['salary'] = salaries
        df.head(100).to_csv('currency_conversion.csv')

file_name = "vacancies_dif_currencies.csv"
process_cur = ProcessCurrencies(file_name)
process_cur.get_currencies_to_convert()
process_cur.generate_currency(process_cur.min_date, process_cur.max_date)
ProcessSalaries(file_name).process_salaries()
