from prettytable import PrettyTable, ALL
import csv
import re
import datetime

class DataSet:
    """
    Считывание файла и формирование удобной структуры данных.

    :param file: Название считываемого файла
    :type file: str

    :param vacancies: Лист вакансий
    :type vacancies: list
    """
    def __init__(self):
        """
        Инициализирует объект класса DataSet.
        """
        self.file = input("Введите название файла: ")
        self.vacancies = [Vacancy(vac) for vac in self.csv_filer(*self.csv_reader(self.file))]

    @staticmethod
    def delete_html(new_html) -> str:
        """
        Функция удаления HTML-тегов и лишних пробелов из поля.

        :param new_html: Очищаемое поле
        :type new_html: str

        :return: Очищенное поле
        :rtype: str

        >>> DataSet.delete_html("abc")
        'abc'
        >>> DataSet.delete_html("<div>abc</div>")
        'abc'
        >>> DataSet.delete_html("<div>abc")
        'abc'
        >>> DataSet.delete_html("   abc  ")
        'abc'
        >>> DataSet.delete_html(" abc     abd")
        'abc abd'
        >>> DataSet.delete_html(" <div><strong><i>  abc <i>  abd  <string>")
        'abc abd'
        >>> DataSet.delete_html(" <div> abc <iqewqljl> <  div   > abd <i>")
        'abc abd'
        """
        result = re.compile(r'<[^>]+>').sub('', new_html)
        return result if '\n' in new_html else " ".join(result.split())

    @staticmethod
    def csv_reader(file) -> tuple:
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
            get_exit("Пустой файл")
        elif len(new_vacancies[1:]) == 0:
            get_exit("Нет данных")
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

    :param salary_gross: Оклад указан до вычета налогов
    :type salary_gross: bool

    :param salary_currency: Идентификатор валюты оклада
    :type salary_currency: str
    """
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """
        Инициализирует объект Salary, переводит зарплату в рубли.

        :param salary_from: Нижняя граница вилки оклада
        :type salary_from: str or int or float

        :param salary_to: Верхняя граница вилки оклада
        :type salary_to: str or int or float

        :param salary_gross: Оклад указан до вычета налогов
        :type salary_gross: bool

        :param salary_currency: Идентификатор валюты оклада
        :type salary_currency: str

        >>> Salary(10.0, 20.4, True, 'RUR').salary_from
        10.0
        >>> Salary(10.0, 20.4, True, 'RUR').salary_to
        20.4
        >>> Salary(10.0, 20.4, True, 'RUR').salary_gross
        True
        >>> Salary(10.0, 20.4, True, 'RUR').salary_currency
        'RUR'
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def to_rub(self, salary: float) -> float:
        """
        Переводит валюту в рубли при помощи словаря currency_to_rub.

        :param salary: Значение оклада
        :type salary: float

        :return: Значение оклада в рублях
        :rtype: float

        >>> Salary(10.0, 20, True, 'RUR').to_rub(10.0 + 20)
        30.0
        >>> Salary(10, 20.0, True, 'RUR').to_rub(10 + 20.0)
        30.0
        >>> Salary(10, 20, True, 'EUR').to_rub(10 + 20)
        1797.0
        >>> Salary(10, 20, True, 'AZN').to_rub(10 + 20)
        1070.4
        """
        return salary * currency_to_rub[self.salary_currency]

class Vacancy:
    """
    Класс для представления вакансии.

    :param name: Название вакансии
    :type name: str

    :param description: Описание вакансии
    :type description: str

    :param key_skills: Навыки
    :type key_skills: list

    :param experience_id: Опыт работы
    :type experience_id: str

    :param premium: Премиум-вакансия
    :type premium: str

    :param employer_name: Название компании
    :type employer_name: str

    :param salary: Оклад вакансий
    :type salary: Salary

    :param area_name: Название региона
    :type area_name: str

    :param published_at: Дата публикации вакансии
    :type published_at: str
    """
    def __init__(self, dict_vac):
        """
        Инициализирует объект класса Vacancy.

        :param dict_vac: Словарь с данными о вакансиях
        :type dict_vac: dict
        """
        self.name = dict_vac['name']
        self.description = dict_vac['description']
        self.key_skills = dict_vac['key_skills'].split('\n')
        self.experience_id = dict_vac['experience_id']
        self.premium = dict_vac['premium']
        self.employer_name = dict_vac['employer_name']
        self.salary = Salary(dict_vac['salary_from'], dict_vac['salary_to'], dict_vac['salary_gross'],
                             dict_vac['salary_currency'])
        self.area_name = dict_vac['area_name']
        self.published_at = dict_vac['published_at']

class InputConect:
    """
    Сбор входных данных, создание таблицы с вакансиями и вывод ее в консоль.

    :param vacs_list: Лист с вакансиями
    :type vacs_list: list

    :param filter_param: Параметр фильтрации
    :type filter_param: str or list

    :param sorting_parameter: Парметр сортировки
    :type sorting_parameter: str

    :param reverse_sort_order: Обратный порядок сортировки
    :type reverse_sort_order: str

    :param vacancies_range: Диапазон вывода вакансий
    :type vacancies_range: list

    :param output_columns: Требуемые столбцы таблицы
    :type output_columns: list
    """
    def __init__(self, vacs_list):
        """
        Инициализация объекта InputCorrect.

        :param vacs_list: Лист с вакансиями
        :type vacs_list: list
        """
        self.vacs_list = vacs_list
        self.filter_param = input("Введите параметр фильтрации: ")
        self.sorting_parameter = input("Введите параметр сортировки: ")
        self.reverse_sort_order = input("Обратный порядок сортировки (Да / Нет): ")
        self.vacancies_range = input("Введите диапазон вывода: ").split()
        self.output_columns = input("Введите требуемые столбцы: ").split(", ")

    def print_vacancies(self) -> None:
        """
        Функция создания таблицы PrettyTable, применение фильтрации и сортировки словарей.

        :return: Выводит таблицу в консоль
        """
        if self.filter_param != '' and ": " not in self.filter_param:
            get_exit("Формат ввода некорректен")
        self.filter_param = self.filter_param.split(": ")
        if self.filter_param[0] not in list(translation_dict.values()) and len(self.filter_param) == 2:
            get_exit("Параметр поиска некорректен")

        self.vacs_list = self.vacs_list if len(self.filter_param) != 2 else get_filter(self.vacs_list,
                                                                                       self.filter_param)

        self.vacs_list = self.vacs_list if len(self.sorting_parameter) == 0 else get_sorting(self.vacs_list,
                                                                                             self.sorting_parameter,
                                                                                             self.reverse_sort_order)
        headers = list(reversed_dict.keys())[:-1]
        field_name = '№'
        headers.insert(0, field_name)
        table = PrettyTable(headers)
        table.hrules = ALL
        if len(self.vacs_list) == 0:
            get_exit("Ничего не найдено")

        for i in range(len(self.vacs_list)):
            vacancies = formatter(self.vacs_list[i])
            vacancies = list(map(lambda i: f'{i[:100]}...' if len(i) > 100 else i, vacancies))
            vacancies.insert(0, i + 1)
            table.add_row(vacancies)

        table.align = 'l'
        table.max_width = 20
        new_start, new_end = get_range(self.vacs_list, self.vacancies_range)

        if self.output_columns[0] != '':
            self.output_columns.insert(0, field_name)
            print(table.get_string(start=new_start, end=new_end, fields=self.output_columns))
        else:
            print(table.get_string(start=new_start, end=new_end))

translation_dict = {"name": "Название","description": "Описание","key_skills": "Навыки","experience_id": "Опыт работы",
                    "premium": "Премиум-вакансия", "employer_name": "Компания",
                    "salary_from": "Нижняя граница вилки оклада", "salary_to": "Верхняя граница вилки оклада",
                    "salary_gross": "Оклад указан до вычета налогов", "salary_currency": "Идентификатор валюты оклада",
                    "area_name": "Название региона", "published_at": "Дата публикации вакансии", "Оклад": "Оклад",

                    "True": "Да", "TRUE": "Да", "False": "Нет", "FALSE": "Нет",

                    "noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет", "between3And6": "От 3 до 6 лет",
                    "moreThan6": "Более 6 лет",

                    "AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро", "GEL": "Грузинский лари",
                    "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли", "UAH": "Гривны",
                    "USD": "Доллары", "UZS": "Узбекский сум"}

reversed_dict = {"Название": "name", "Описание": "description", "Навыки": "key_skills", "Опыт работы": "experience_id",
                 "Премиум-вакансия": "premium", "Компания": "employer_name", "Оклад": "Оклад",
                 "Название региона": "area_name", "Дата публикации вакансии": "published_at",
                 "Идентификатор валюты оклада": "salary_currency"}

currency_to_rub = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76,
                   "KZT": 0.13, "RUR": 1, "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}

exp_values = {"noExperience": 0, "between1And3": 1, "between3And6": 2, "moreThan6": 3}

def get_exit(message) -> None:
    """
    Преднамеренное завершение программы с выводом сообщения в консоль.

    :param message: Текст сообщения
    :type message: str

    :return: Завершает программу
    """
    print(message)
    exit()

def get_data(date) -> str:
    """
    Функция для записи даты публикации вакансии в правильном формате.

    :param date: Дата публикации вакансии
    :type date: str

    :return: Отформатированная дата
    :rtype: str

    >>> get_data('2022-05-31T17:32:49+0300')
    '31.05.2022'
    """
    new_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
    return new_date.strftime('%d.%m.%Y')

def formatter(new_vacancy: Vacancy) -> list:
    """
    Функция для форматирования данных в словаре вакансий.

    :param new_vacancy: Лист с вакансиями
    :type new_vacancy: Vacancy

    :return: Отформатированный лист с вакансиями
    :rtype: list
    """

    def get_salary(new_salary: Salary) -> str:
        """
        Функция для записи оклада в правильном формате.

        :param new_salary: Оклад вакансии
        :type: Salary

        :return: Отформатированный оклад
        :rtype: str
        """
        lower_salary = int(float(new_salary.salary_from))
        lower_salary = '{0:,}'.format(lower_salary).replace(',', ' ')
        upper_salary = int(float(new_salary.salary_to))
        upper_salary = '{0:,}'.format(upper_salary).replace(',', ' ')

        new_currency = translation_dict[new_salary.salary_currency]
        tax = "С вычетом налогов" if translation_dict[new_salary.salary_gross] == 'Нет' else "Без вычета налогов"

        result = f'{lower_salary} - {upper_salary} ({new_currency}) ({tax}) '
        return result

    return [new_vacancy.name, new_vacancy.description, '\n'.join(new_vacancy.key_skills),
            translation_dict[new_vacancy.experience_id], translation_dict[new_vacancy.premium],
            new_vacancy.employer_name, get_salary(new_vacancy.salary), new_vacancy.area_name,
            get_data(new_vacancy.published_at)]

def get_filter(list_vacs, filter_param) -> list:
    """
    Функция для фильтрации данных в зависимости от параметра фильтрации.

    :param list_vacs: Лист вакансий
    :type list_vacs: list

    :param filter_param: Параметр фильтрации
    :type filter_param: list

    :return: Отфильтрованный лист вакансий
    :rtype: list
    """
    if filter_param[0] == 'Оклад':
        list_vacancies = list(filter(lambda item: int(item.salary.salary_from) <= int(filter_param[1]) <= int(item.salary.salary_to),
                                                            list_vacs))
    elif filter_param[0] == 'Дата публикации вакансии':
        list_vacancies = list(filter(lambda item: filter_param[1] == datetime.datetime.strptime(item.published_at,
                         '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y'), list_vacs))

    elif filter_param[0] == 'Навыки':
        list_vacancies = list(filter(lambda vac: all(item in vac.key_skills for item in filter_param[1].split(', ')),
                                     list_vacs))
    elif filter_param[0] == 'Идентификатор валюты оклада':
        list_vacancies = list(filter(lambda item: filter_param[1] == translation_dict[item.salary.salary_currency],
                                     list_vacs))

    elif filter_param[0] == 'Премиум-вакансия' or filter_param[0] == 'Опыт работы':
        list_vacancies = list(filter(lambda item: filter_param[1] == translation_dict[item.__getattribute__(reversed_dict[filter_param[0]])],
                                     list_vacs))
    else:
        list_vacancies=list(filter(lambda vac: filter_param[1] == vac.__getattribute__(reversed_dict[filter_param[0]]),
                                     list_vacs))
    return list_vacancies

def get_range(table, vacancies_range) -> tuple:
    """
    Функция для получения начального и конечного индекса отображения таблицы.

    :param table: Данные для таблицы
    :type table: list

    :param vacancies_range: Диапазон вывода вакансий
    :type vacancies_range: list

    :return: Начальный и конечный индекс для отображения таблицы
    :rtype: tuple
    """
    new_start, new_end = 0, len(table)
    if len(vacancies_range) == 0:
        return new_start, new_end
    elif len(vacancies_range) == 2:
        new_start, new_end = int(vacancies_range[0]) - 1, int(vacancies_range[1]) - 1
    else:
        new_start = int(vacancies_range[0]) - 1
    return new_start, new_end

def get_sorting(list_to_sort, sorting_param, reverse_sort_order) -> list:
    """
    Функция для сортировки данных и проверки входных данных для сортировки.

    :param list_to_sort: Лист вакансий для сортировки
    :type list_to_sort: list

    :param sorting_param: Парметр сортировки
    :type sorting_param: str

    :param reverse_sort_order: Обратный порядок сортировки
    :type reverse_sort_order: str

    :return: Отсортированный лист вакансий
    :rtype: list
    """
    if len(sorting_param) == 0:
        return list_to_sort
    elif sorting_param not in list(translation_dict.values()):
        get_exit("Параметр сортировки некорректен")
    elif reverse_sort_order != "Да" and reverse_sort_order != "Нет" and reverse_sort_order != "":
        get_exit("Порядок сортировки задан некорректно")

    reverse = True if reverse_sort_order == "Да" else False

    if sorting_param == 'Навыки':
        return sorted(list_to_sort, key=lambda item: len(item.key_skills), reverse=reverse)

    elif sorting_param == 'Оклад':
        return sorted(list_to_sort, key=lambda item: item.salary.to_RUB(float(item.salary.salary_from) + float(item.salary.salary_to)) / 2, reverse=reverse)

    elif sorting_param == 'Опыт работы':
        return sorted(list_to_sort, key=lambda item: exp_values[item.experience_id], reverse=reverse)

    else:
        return sorted(list_to_sort,key=lambda item: item.__getattribute__(reversed_dict[sorting_param]),reverse=reverse)

def create_table() -> None:
    """
    Функция для создания и вывода таблицы PrettyTable.

    :return: Вывод таблицы в консоль
    """
    new_data = DataSet()
    result = InputConect(new_data.vacancies)
    result.print_vacancies()

if __name__ == '__main__':
    create_table()
