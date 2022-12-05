from prettytable import PrettyTable, ALL
import csv
import re
import datetime

class DataSet:
    def __init__(self):
        self.file = input("Введите название файла: ")
        self.vacancies = [Vacancy(vac) for vac in self.csv_filer(*self.csv_reader(self.file))]

    def delete_html(self, new_html):
        result = re.compile(r'<[^>]+>').sub('', new_html)
        return result if '\n' in new_html else " ".join(result.split())

    def csv_reader(self, file):
        reader = csv.reader(open(file, encoding='utf_8_sig'))
        new_vacancies = [row for row in reader]
        if len(new_vacancies) == 0:
            get_exit("Пустой файл")
        elif len(new_vacancies[1:]) == 0:
            get_exit("Нет данных")
        else:
            return new_vacancies[0], new_vacancies[1:]

    def csv_filer(self, headers, vacancies):
        vacancies_list = list(filter(lambda vac: (len(vac) == len(headers) and vac.count('') == 0), vacancies))
        vacanies_dictionary = [dict(zip(headers, map(self.delete_html, vac))) for vac in vacancies_list]
        return vacanies_dictionary

class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def to_RUB(self, salary: float) -> float:
        return salary * currency_to_rub[self.salary_currency]

class Vacancy:
    def __init__(self, dict_vac):
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
    def __init__(self, vacs_list):
        self.vacs_list = vacs_list
        self.filter_param = input("Введите параметр фильтрации: ")
        self.sorting_parameter = input("Введите параметр сортировки: ")
        self.reverse_sort_order = input("Обратный порядок сортировки (Да / Нет): ")
        self.vacancies_range = input("Введите диапазон вывода: ").split()
        self.output_columns = input("Введите требуемые столбцы: ").split(", ")

    def print_vacancies(self) -> None:
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

def get_exit(message):
    print(message)
    exit()

def formatter(new_vacancy: Vacancy):
    def get_data(date):
        new_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        return new_date.strftime('%d.%m.%Y')

    def get_salary(new_salary: Salary):
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

def get_filter(list_vacs, filter_param):
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

def get_range(table, vacancies_range):
    new_start, new_end = 0, len(table)
    if len(vacancies_range) == 0:
        return new_start, new_end
    elif len(vacancies_range) == 2:
        new_start, new_end = int(vacancies_range[0]) - 1, int(vacancies_range[1]) - 1
    else:
        new_start = int(vacancies_range[0]) - 1
    return new_start, new_end

def get_sorting(list_to_sort, sorting_param, reverse_sort_order):
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

def create_table():
    new_data = DataSet()
    result = InputConect(new_data.vacancies)
    result.print_vacancies()


if __name__ == '__main__':
    create_table()
