import csv
import re
import datetime
from typing import List
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from jinja2 import Template
import pdfkit
#Меняю файл в ветке develop

class DataSet:
    """
    Считывание файла и формирование удобной структуры данных.

    :param file: Название считываемого файла
    :type file: str

    :param vacancies: Лист вакансий
    :type vacancies: list

    :param vacancy_name: Название профессии
    :type vacancy_name: str
    """
    def __init__(self):
        """
        Инициализирует объект класса DataSet.
        """
        self.file = input("Введите название файла: ")
        self.vacancy_name = input("Введите название профессии: ")
        self.vacancies = [Vacancy(vac) for vac in self.csv_filer(*self.csv_reader(self.file))]

    def delete_html(self, new_html) -> str:
        """
        Функция удаления HTML-тегов и лишних пробелов из поля.

        :param new_html: Очищаемое поле
        :type new_html: str

        :return: Очищенное поле
        :rtype: str
        """
        result = re.compile(r'<[^>]+>').sub('', new_html)
        return result if '\n' in new_html else " ".join(result.split())

    def csv_reader(self, file) -> tuple:
        """
        Считывание csv-файла с проверкой есть ли данные в файле.

        :param file: Название считываемого файла
        :type file: str

        :return: Заголовки файла и данные о вакансиях
        :rtype: tuple
        """
        reader = csv.reader(open(file, encoding='utf_8_sig'))
        new_vacancies = [row for row in reader]
        if len(new_vacancies) == 0:
            print("Пустой файл")
            exit()
        elif len(new_vacancies[1:]) == 0:
            print("Нет данных")
            exit()
        else:
            return new_vacancies[0], new_vacancies[1:]

    def csv_filer(self, headers, vacancies) -> list:
        """
        Отчищает лист вакансий от пустых элементов, создает словарь вакансий.

        :param headers: Заголовки csv файла
        :type headers: list

        :param vacancies: Описания вакансий
        :type vacancies: list

        :return: Лист со словарями для каждой вакансии
        :rtype: list
        """
        vacancies_list = list(filter(lambda vac: (len(vac) == len(headers) and vac.count('') == 0), vacancies))
        vacanies_dictionary = [dict(zip(headers, map(self.delete_html, vac))) for vac in vacancies_list]
        return vacanies_dictionary

class Salary:
    """
    Класс для представления зарплаты.

    :param salary_from: Нижняя граница вилки оклада
    :type salary_from: str or int or float

    :param salary_to: Верхняя граница вилки оклада
    :type salary_to: str or int or float

    :param salary_currency: Идентификатор валюты оклада
    :type salary_currency: str
    """
    def __init__(self, salary_from, salary_to, salary_currency):
        """
        Инициализирует объект Salary, переводит зарплату в рубли.

        :param salary_from: Нижняя граница вилки оклада
        :type salary_from: str or int or float

        :param salary_to: Верхняя граница вилки оклада
        :type salary_to: str or int or float

        :param salary_gross: Оклад указан до вычета налогов
        :type salary_gross: str

        :param salary_currency: Идентификатор валюты оклада
        :type salary_currency: str
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency

    def to_rub(self, new_salary: float) -> float:
        """
        Переводит валюту в рубли при помощи словаря currency_to_rub.

        :param new_salary: Значение оклада
        :type new_salary: float

        :return: Значение оклада в рублях
        :rtype: float
        """
        return new_salary * currency_to_rub[self.salary_currency]

class Vacancy:
    """
    Класс для представления вакансии.

    :param name: Название вакансии
    :type name: str

    :param salary: Оклад вакансий
    :type salary: Salary

    :param area_name: Название региона
    :type area_name: str

    :param published_at: Дата публикации вакансии
    :type published_at: str
    """
    def __init__(self, dictionary):
        """
        Инициализирует объект класса Vacancy.

        :param dictionary: Словарь с данными о вакансиях
        :type dictionary: dict
        """
        self.name = dictionary['name']
        self.salary = Salary(dictionary['salary_from'], dictionary['salary_to'], dictionary['salary_currency'])
        self.area_name = dictionary['area_name']
        self.published_at = dictionary['published_at']

class Report:
    """
    Класс для создания png-графиков и pdf-файла.

    :param vacancy_name: Название вакансии
    :type vacancy_name: str

    :param years_salary: Динамика уровня зарплат по годам
    :type years_salary: dict

    :param years_vacs_count: Динамика количества вакансий по годам
    :type years_vacs_count: dict

    :param prof_years_salary: Динамика уровня зарплат по годам для выбранной профессии
    :type prof_years_salary: dict

    :param prof_years_vacs_count: Динамика количества вакансий по годам для выбранной профессии
    :type prof_years_vacs_count: dict

    :param city_salary: Уровень зарплат по городам
    :type city_salary: dict

    :param city_vacs_rate: Доля вакансий по городам
    :type city_vacs_rate: dict

    :param years_sheet_headers: Заголовки для таблицы по годам
    :type years_sheet_headers: list

    :param years_sheet_rows: Строки для таблицы по годам
    :type years_sheet_rows: list

    :param city_sheet_headers: Заголовки для таблицы по городам
    :type city_sheet_headers: list

    :param city_sheet_rows: Строки для таблицы по городам
    :type city_sheet_rows: list
    """
    def __init__(self, vacancy_name, years_salary, years_vacs_count, prof_years_salary, prof_years_vacs_count,
                 city_salary, city_vacs_rate):
        """
        Инициализация класса Report. Структурирование данных для графиков и таблиц.

        :param vacancy_name: Название вакансии
        :type vacancy_name: str

        :param years_salary: Динамика уровня зарплат по годам
        :type years_salary: dict

        :param years_vacs_count: Динамика количества вакансий по годам
        :type years_vacs_count: dict

        :param prof_years_salary: Динамика уровня зарплат по годам для выбранной профессии
        :type prof_years_salary: dict

        :param prof_years_vacs_count: Динамика количества вакансий по годам для выбранной профессии
        :type prof_years_vacs_count: dict

        :param city_salary: Уровень зарплат по городам
        :type city_salary: dict

        :param city_vacs_rate: Доля вакансий по городам
        :type city_vacs_rate: dict
        """
        self.vacancy_name = vacancy_name
        self.years_salary = years_salary
        self.years_vacs_count = years_vacs_count
        self.prof_years_salary = prof_years_salary
        self.prof_years_vacs_count = prof_years_vacs_count
        self.city_salary = city_salary
        self.city_vacs_rate = city_vacs_rate
        self.years_sheet_headers = ['Год', 'Средняя зарплата', 'Средняя зарплата - Программист', 'Количество вакансий',
                               'Количество вакансий - Программист']
        years_sheet_columns = [list(years_salary.keys()), list(years_salary.values()),
                           list(years_vacs_count.values()), list(prof_years_salary.values()),
                           list(prof_years_vacs_count.values())]
        self.years_sheet_rows = self.get_table_rows(years_sheet_columns)
        self.city_sheet_headers = ['Город', 'Уровень зарплат', ' ', 'Город', 'Доля вакансий']
        city_sheet_columns = [list(city_salary.keys()), list(city_salary.values()),
                           ["" for _ in city_salary.keys()], list(city_vacs_rate.keys()),
                           list(map(self.get_percents, city_vacs_rate.values()))]
        self.city_sheet_rows = self.get_table_rows(city_sheet_columns)

    def get_percents(self, value) -> str:
        """
        Функция для получения процентов.

        :param value: Значение которое нужно перевести в проценты
        :type value: int or float

        :return: Значение в процентах
        :rtype: str
        """
        return f"{round(value * 100, 2)}%"

    def get_table_rows(self, columns: list) -> list:
        """
        Функция для транспанирования списка списков - первод столбцов в строки.

        :param columns: Список столбцов
        :type columns: list

        :return: Список строк
        :rtype: list
        """
        rows_list = [["" for _ in range(len(columns))] for _ in range(len(columns[0]))]
        for col in range(len(columns)):
            for cell in range(len(columns[col])):
                rows_list[cell][col] = columns[col][cell]
        return rows_list

    def create_regular_schedule(self, ax: Axes, keys1, keys2, values1, values2, label1, label2, title) -> None:
        """
        Функция для создания 2-х обычных столбчатых диаграмм на одном поле.

        :param ax: Глобальная позиция графика (поле для рисования)
        :type ax: Axes

        :param keys1: Значения по оси Х для первого графика
        :type keys1: _dict_keys

        :param keys2: Значения по оси Х для второго графика
        :type keys2: _dict_keys

        :param values1: Значения по оси У для первого графика
        :type values1: _dict_values

        :param values2: Значения по оси У для второго графика
        :type values2: _dict_values

        :param label1: Легенда первого графика
        :type label1: str

        :param label2: Легенда второго графика
        :type label2: str

        :param title: Название поля
        :type title: str

        :return: 2 обычные столбчатые диаграммы на одном поле
        """
        x1 = [key - 0.2 for key in keys1]
        x2 = [key + 0.2 for key in keys2]
        ax.bar(x1, values1, width=0.4, label=label1)
        ax.bar(x2, values2, width=0.4, label=label2)
        ax.legend()
        ax.set_title(title, fontsize=16)
        ax.grid(axis="y")
        ax.tick_params(axis="x", labelrotation=90)

    def create_pie_schedule(self, ax: Axes, title) -> None:
        """
        Функция создания круговой диаграммы.

        :param ax: Глобальная позиция графика (поле для рисования)
        :type ax: Axes

        :param title: Название поля
        :type title: str

        :return: Круговая диаграмма
        """
        new_dict = self.city_vacs_rate
        new_dict["Другие"] = 1 - sum([value for value in new_dict.values()])
        ax.pie(x=list(new_dict.values()), labels=list(new_dict.keys()))
        ax.axis('equal')
        ax.tick_params(axis="both", labelsize=6)
        plt.rcParams['font.size'] = 16
        ax.set_title(title, fontsize=16)

    def create_horizontal_schedule(self, ax: Axes, keys, values, title) -> None:
        """
        Функция создания горизонтальной диаграммы.

        :param ax: Глобальная позиция графика (поле для рисования)
        :type ax: Axes

        :param keys: Значения по оси Х
        :type keys: _dict_keys

        :param values: Значения по оси У
        :type values: _dict_values

        :param title: Название поля
        :type title: str

        :return:
        """
        keys = [key.replace(" ", "\n").replace("-", "-\n") for key in list(keys)]
        ax.barh(keys, values)
        ax.set_yticks(keys)
        ax.set_yticklabels(labels=keys, verticalalignment="center", horizontalalignment="right")
        ax.invert_yaxis()
        ax.set_title(title, fontsize=16)
        ax.grid(axis="x")
        ax.tick_params(axis='y', labelsize=6)

    def generate_schedule(self) -> None:
        """
        Функция для создания png-файла с графиками.

        :return: png-файл с графиками
        """
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.create_regular_schedule(axis[0, 0], self.years_salary.keys(), self.prof_years_salary.keys(),
                                     self.years_salary.values(), self.prof_years_salary.values(),
                                     "Средняя з/п", "з/п программист", "Уровень зарплат по годам")

        self.create_regular_schedule(axis[0, 1], self.years_vacs_count.keys(), self.prof_years_vacs_count.keys(),
                            self.years_vacs_count.values(), self.prof_years_vacs_count.values(),
                            "Количество вакансий", "Количество вакансий программист", "Количество вакансий по годам")

        self.create_horizontal_schedule(axis[1, 0], self.city_salary.keys(), self.city_salary.values(),
                                        "Уровень зарплат по городам")

        self.create_pie_schedule(axis[1, 1], "Доля вакансий по городам")

        fig.set_size_inches(16, 9)
        fig.tight_layout(h_pad=2)
        fig.savefig("graph.png")

    def generate_pdf(self) -> None:
        """
        Функция для генерации pdf-файла из получившихся данных, png-графиков, и HTML-шаблона.

        :return: PDF-файл с данными
        """
        self.generate_schedule()
        html = open("pdf_template.html").read()
        template = Template(html)
        keys_to_values = {
            "title": "Аналитика по зарплатам и городам для профессии " + self.vacancy_name,
            "image_name": "graph.png",
            "years_title": "Статистика по годам",
            "years_headers": self.years_sheet_headers,
            "years_rows": self.years_sheet_rows,
            "cities_title": "Статистика по городам",
            "cities_headers": self.city_sheet_headers,
            "count_columns": len(self.city_sheet_headers),
            "cities_rows": self.city_sheet_rows
        }
        pdf_template = template.render(keys_to_values)
        config = pdfkit.configuration(wkhtmltopdf=r"D:\For PDF python\wkhtmltopdf\bin\wkhtmltopdf.exe")
        pdfkit.from_string(pdf_template, "report.pdf", configuration=config, options={"enable-local-file-access": True})


currency_to_rub = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76,
                   "KZT": 0.13, "RUR": 1, "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}

def get_data(date) -> int:
    """
    Функция для записи даты публикации вакансии в правильном формате.

    :param date: Дата публикации вакансии
    :type date: str

    :return: Отформатированная дата
    :rtype: int
    """
    new_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
    return int(new_date.strftime('%Y'))

def get_statistic(result, index, new_message, slice=0, reverse=False) -> dict:
    """
    Функция для получения общей статистики.

    :param result: Результат предыдущей операции (словарь)
    :type result: _dict_items

    :param index: Индекс в словаре
    :type index: int

    :param new_message: Сообщение которое выводится в консоль вместе со словарем
    :type new_message: str

    :param slice: Ограничение по значениям (максимум 10)
    :type slice: int

    :param reverse: Обратный порядок статистики
    :type reverse: bool

    :return: Словарь с итоговой статистикой
    :rtype: dict
    """
    slice = len(result) if slice == 0 else slice
    statistic = dict(sorted(result, key=lambda item: item[index], reverse=reverse)[:slice])
    print(f'{new_message}{str(statistic)}')
    return statistic

def get_salary_statistic(vacs_list: List[Vacancy], field, vac_name: str = '') -> dict:
    """
    Функция для получения словаря со статистикой по окладу.

    :param vacs_list: Лист с вакансиями
    :type vacs_list: list

    :param field: Поле, по которому будет выполняться статистика
    :type field: str

    :param vac_name: Название вакансии
    :type vac_name: str

    :return: Словарь со статистикой по окладу
    :rtype: dict
    """
    statistic_result = {}
    for vac in vacs_list:
        if vac.__getattribute__(field) not in statistic_result.keys():
            statistic_result[vac.__getattribute__(field)] = []
    if vac_name != '':
        vacs_list = list(filter(lambda item: vac_name in item.name, vacs_list))

    for vac in vacs_list:
        salary_to = vac.salary.salary_to
        salary_from = vac.salary.salary_from
        statistic_result[vac.__getattribute__(field)].append(
            vac.salary.to_rub(float(salary_from) + float(salary_to)) / 2)

    for key in statistic_result.keys():
        statistic_result[key] = int(sum(statistic_result[key]) // len(statistic_result[key])) if len(
            statistic_result[key]) != 0 else 0

    return statistic_result

def get_vacancies_statistic(vacs_list: List[Vacancy], length, field, vac_name: str = '') -> dict:
    """
    Функция для получения словаря со статистикой по вакансиям.

    :param vacs_list: Лист с вакансиями
    :type vacs_list: list

    :param length: Длина
    :type length: int

    :param field: Поле, по которому будет выполняться статистика
    :type field: str

    :param vac_name: Название вакансии
    :type vac_name: str

    :return: Словарь со статистикой по вакансиям
    :rtype: dict
    """
    statistic_result = {}
    for vac in vacs_list:
        if vac.__getattribute__(field) not in statistic_result.keys():
            statistic_result[vac.__getattribute__(field)] = 0

    if vac_name != '':
        vacs_list = list(filter(lambda item: vac_name in item.name, vacs_list))
    for vac in vacs_list:
        statistic_result[vac.__getattribute__(field)] += 1

    if field == 'area_name':
        for key in statistic_result.keys():
            statistic_result[key] = round(statistic_result[key] / length, 4)

    return statistic_result

def create_report() -> None:
    """
    Функция создания pdf-файла-отчета.

    :return: PDF-файл с отчетом
    """
    new_data = DataSet()
    new_dict = {}

    for vacs in new_data.vacancies:
        vacs.published_at = get_data(vacs.published_at)
        if vacs.area_name not in new_dict.keys():
            new_dict[vacs.area_name] = 0
        new_dict[vacs.area_name] += 1

    needed_vacs = list(
        filter(lambda x: int(len(new_data.vacancies) * 0.01) <= new_dict[x.area_name], new_data.vacancies))
    years_salary = get_statistic(get_salary_statistic(new_data.vacancies, 'published_at').items(), 0,
                                 'Динамика уровня зарплат по годам: ')
    years_vacs_count = get_statistic(get_vacancies_statistic(new_data.vacancies, len(new_data.vacancies), 'published_at').items(), 0,
                                     'Динамика количества вакансий по годам: ')
    prof_years_salary = get_statistic(get_salary_statistic(new_data.vacancies, 'published_at', new_data.vacancy_name).items(), 0,
        'Динамика уровня зарплат по годам для выбранной профессии: ')
    prof_years_vacs_count = get_statistic(
        get_vacancies_statistic(new_data.vacancies, len(new_data.vacancies), 'published_at', new_data.vacancy_name).items(), 0,
        'Динамика количества вакансий по годам для выбранной профессии: ')
    city_salary = get_statistic(get_salary_statistic(needed_vacs, 'area_name').items(), 1,
                                'Уровень зарплат по городам (в порядке убывания): ', 10, True)
    city_vacs_rate = get_statistic(get_vacancies_statistic(needed_vacs, len(new_data.vacancies), 'area_name').items(),1,
                                   'Доля вакансий по городам (в порядке убывания): ', 10, True)

    report = Report(new_data.vacancy_name, years_salary, years_vacs_count, prof_years_salary, prof_years_vacs_count,
                    city_salary, city_vacs_rate)
    report.generate_pdf()

if __name__ == '__main__':
    create_report()
