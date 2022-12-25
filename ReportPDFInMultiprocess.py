import time
import csv
import math
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import multiprocessing as mp
from jinja2 import Template
import pdfkit

currency_to_rub = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76,
                   "KZT": 0.13, "RUR": 1, "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}

class InputCorrect:
    """
    Проверка существования и заполненности файла.

    :param file: Название считываемого файла
    :type file: str

    :param prof: Название профессии
    :type prof: str
    """
    def __init__(self, file: str, prof: str):
        """
        Инициализация объекта InputCorrect. Проверка на существование и заполненность файла.

        :param file: Название считываемого файла
        :type file: str

        :param prof: Название профессии
        :type prof: str
        """
        self.file_name = file
        self.prof = prof
        self.check_file()

    def check_file(self) -> None:
        """
        Проверка на существование и заполненность файла.
        """
        with open(self.file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file_iter = iter(csv.reader(csv_file))
            if next(file_iter, "none") == "none":
                print("Пустой файл")
                exit()

class Salary:
    """
    Класс для представления зарплаты.

    :param dictionary: Словарь информации о зарплате
        :type dictionary: dict
    """
    def __init__(self, dictionary):
        """
        Инициализирует объект Salary, переводит зарплату в рубли.

        :param dictionary: Словарь информации о зарплате
        :type dictionary: dict
        """
        self.salary_from = math.floor(float(dictionary["salary_from"]))
        self.salary_to = math.floor(float(dictionary["salary_to"]))
        self.salary_currency = dictionary["salary_currency"]
        middle_salary = (self.salary_to + self.salary_from) / 2
        self.salary_in_rur = currency_to_rub[self.salary_currency] * middle_salary

class Vacancy:
    """
    Класс для представления вакансии.

    :param dictionary: Словарь информации о зарплате
    :type dictionary: dict
    """
    def __init__(self, dictionary: dict):
        """
        Инициализация объекта Vacancy. Приведение к более удобному виду.

        :param dictionary: Словарь информации о зарплате
        :type dictionary: dict
        """
        self.dictionary = dictionary
        self.salary = Salary(dictionary)
        self.dictionary["year"] = int(dictionary["published_at"][:4])
        self.is_needed = dictionary["is_needed"]

class DataSet:
    """
    Считывание файла и формирование удобной структуры данных.

    :param csv_dir: Папка расположения всех csv-файлов
    :type csv_dir: str

    :param data_set: Данные в удобном формате
    :type data_set: str
    """
    def __init__(self, csv_dir: str, prof: str, file_name: str):
        """
        Инициализация класса DataSet. Чтение. Фильтрация. Форматирование.

        :param csv_dir: Папка расположения всех csv-файлов
        :type csv_dir: str

        :param data_set: Данные в удобном формате
        :type data_set: str
        """
        self.csv_dir = csv_dir
        self.prof = prof
        self.start_line = []
        self.year_to_count = {}
        self.year_to_salary = {}
        self.year_to_count_needed = {}
        self.year_to_salary_needed = {}
        self.area_to_salary = {}
        self.area_to_piece = {}
        area_to_sum, area_to_count = self.csv_divide(file_name)
        self.count_area_data(area_to_sum, area_to_count)
        self.sort_year_dicts()

    def csv_reader(self, read_queue: mp.Queue) -> None:
        """
        Чтение данных и складывание их результатов воедино.

        :param read_queue: Oчередь из данных
        :type read_queue: Queue
        """
        while not read_queue.empty():
            data = read_queue.get()
            self.year_to_count[data[0]] = data[1]
            self.year_to_salary[data[0]] = data[2]
            self.year_to_count_needed[data[0]] = data[3]
            self.year_to_salary_needed[data[0]] = data[4]

    def save_file(self, current_year: str, lines: list) -> str:
        """
        Сохраняет CSV-файл с конкретными годами.

        :param current_year: Текущий год
        :type current_year: str

        :param lines: Список вакансий этого года
        :type lines: list

        :return: CSV-файл с конкретными годами
        :rtype: str
        """
        file_name = f"file_{current_year}.csv"
        with open(f"{self.csv_dir}/{file_name}", "w", encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines)
        return file_name

    @staticmethod
    def try_to_add(dic: dict, key, val) -> dict:
        """
        Попытка добавить в словарь значение по ключу или создать новый ключ, если его не было.

        :param dic: Словарь, в который добавляется ключ или значение по ключу
        :type dic: dict

        :param key: Ключ
        :param val: Значение

        :return: Изменный словарь
        :rtype: dict
        """
        try:
            dic[key] += val
        except:
            dic[key] = val
        return dic

    def read_one_csv_file(self, queue: mp.Queue, file_name: str) -> None:
        """
        Читает один csv-файл и делает данные о нём.

        :param queue: Очередь для добавления данных
        :type queue: Queue

        :param file_name: Файл, из которого идет чтение
        :type file_name: str
        """
        print("start: "+file_name)
        with open(f"{self.csv_dir}/{file_name}", "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            filtered_vacs = []
            year = int(file_name.replace("file_", "").replace(".csv", ""))
            for line in file:
                new_dict_line = dict(zip(self.start_line, line))
                new_dict_line["is_needed"] = (new_dict_line["name"]).find(self.prof) > -1
                vac = Vacancy(new_dict_line)
                filtered_vacs.append(vac)
            csv_file.close()
            all_count = len(filtered_vacs)
            all_sum = sum([vac.salary.salary_in_rur for vac in filtered_vacs])
            all_middle = math.floor(all_sum / all_count)
            needed_vacs = list(filter(lambda vacancy: vacancy.is_needed, filtered_vacs))
            needed_count = len(needed_vacs)
            needed_sum = sum([vac.salary.salary_in_rur for vac in needed_vacs])
            needed_middle = math.floor(needed_sum / needed_count)
            queue.put((year, all_count, all_middle, needed_count, needed_middle))
        print("stop: " + file_name)

    def csv_divide(self, file_name: str):
        """
        Разделяет данные на csv-файлы по годам.
        """
        read_queue = mp.Queue()
        area_to_sum = {}
        area_to_count = {}
        procs = []
        with open(file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            year_index = self.start_line.index("published_at")
            next_line = next(file)
            current_year = int(next_line[year_index][:4])
            data_years = [next_line]
            for line in file:
                if not ("" in line) and len(line) == len(self.start_line):
                    new_dict_line = dict(zip(self.start_line, line))
                    new_dict_line["is_needed"] = None
                    vac = Vacancy(new_dict_line)
                    area_to_sum = DataSet.try_to_add(area_to_sum, vac.dictionary["area_name"], vac.salary.salary_in_rur)
                    area_to_count = DataSet.try_to_add(area_to_count, vac.dictionary["area_name"], 1)
                    if vac.dictionary["year"] != current_year:
                        new_csv = self.save_file(current_year, data_years)
                        data_years = []
                        print("save " + str(current_year))
                        proc = mp.Process(target=self.read_one_csv_file, args=(read_queue, new_csv))
                        proc.start()
                        procs.append(proc)
                        current_year = vac.dictionary["year"]
                    data_years.append(line)
            new_csv = self.save_file(str(current_year), data_years)
            proc = mp.Process(target=self.read_one_csv_file, args=(read_queue, new_csv))
            procs.append(proc)
            proc.start()
            csv_file.close()
            for proc in procs:
                proc.join()
            self.csv_reader(read_queue)
            return area_to_sum, area_to_count

    @staticmethod
    def get_sorted_dict(key_to_salary: dict) -> dict:
        """
        Сортирует словарь по значениям по убыванию и только 10 ключ-значений.

        :param key_to_salary: Неотсортированный словарь
        :type key_to_salary: dict

        :return: Отсортированный словарь, в котором только 10 ключ-значений
        :rtype: dict
        """
        return dict(list(sorted(key_to_salary.items(), key=lambda item: item[1], reverse=True))[:10])

    @staticmethod
    def sort_dict_for_keys(dictionary: dict) -> dict:
        """
        Возвращает отсортированный по ключам словарь.

        :param dictionary: Неотсортированный словарь
        :type dictionary: dict

        :return: Отсортированный словарь
        :rtype: dict
        """
        return dict(sorted(dictionary.items(), key=lambda item: item[0]))

    def sort_year_dicts(self):
        """
        Сортировка полученных данных.
        """
        self.year_to_count = DataSet.sort_dict_for_keys(self.year_to_count)
        self.year_to_salary = DataSet.sort_dict_for_keys(self.year_to_salary)
        self.year_to_count_needed = DataSet.sort_dict_for_keys(self.year_to_count_needed)
        self.year_to_salary_needed = DataSet.sort_dict_for_keys(self.year_to_salary_needed)
        self.area_to_piece = DataSet.get_sorted_dict(self.area_to_piece)
        self.area_to_salary = DataSet.get_sorted_dict(self.area_to_salary)

    @staticmethod
    def get_middle_salary(key_to_count: dict, key_to_sum: dict) -> dict:
        """
        Получает словарь со средними зарплатами.

        :param key_to_count: Словарь ключ/кол-во повторений
        :type key_to_count: dict

        :param key_to_sum: Словарь ключ/сумма
        :type key_to_sum: dict

        :return: Словарь с теми же ключами, но значения по ключам - средняя зарплата
        :rtype: dict
        """
        key_to_salary = {}
        for key, val in key_to_count.items():
            if val == 0:
                key_to_salary[key] = 0
            else:
                key_to_salary[key] = math.floor(key_to_sum[key] / val)
        return key_to_salary

    @staticmethod
    def get_area_to_salary_and_piece(area_to_sum: dict, area_to_count: dict) -> tuple:
        """
        Универсальная функция для высчитывания средней зарплаты и количества по ключам.

        :param area_to_sum: Словарь город/сумма зарплаты в нем
        :type area_to_sum: dict

        :param area_to_count: ловарь город/кол-во вакансий в нем
        :type area_to_count: dict

        :return: Кортеж из двух словарей: город/средняя зарплата, город/доля вакансий
        :rtype: tuple
        """
        vacs_count = sum(area_to_count.values())
        area_to_count = dict(filter(lambda item: item[1] / vacs_count > 0.01, area_to_count.items()))
        area_to_middle_salary = DataSet.get_middle_salary(area_to_count, area_to_sum)
        area_to_piece = {key: round(val / vacs_count, 4) for key, val in area_to_count.items()}
        return area_to_middle_salary, area_to_piece

    def count_area_data(self, area_to_sum: dict, area_to_count: dict) -> None:
        """
        Считает дополнительные данные для графиков и таблиц.

        :param area_to_sum: Словарь город/сумма зарплаты в нем
        :type area_to_sum: dict

        :param area_to_count: Cловарь город/кол-во вакансий в нем
        :type area_to_count: dict
        """
        self.area_to_salary, self.area_to_piece = \
            DataSet.get_area_to_salary_and_piece(area_to_sum, area_to_count)

class Report:
    """
    Класс для создания png-графиков и pdf-файла.

    :param data: Посчитанные данные для графиков
    :type data: DataSet
    """
    def __init__(self, data: DataSet):
        """
        Инициализация класса Report. Структурирование данных для графиков и таблиц.

        :param data: Посчитанные данные для графиков
        :type data: DataSet
        """
        self.data = data
        self.years_sheet_headers = ["Год", "Средняя зарплата", "Средняя зарплата - Программист",
                                "Количество вакансий", "Количество вакансий - Программист"]
        years_sheet_columns = [list(data.year_to_salary.keys()), list(data.year_to_salary.values()),
                           list(data.year_to_salary_needed.values()), list(data.year_to_count.values()),
                           list(data.year_to_count_needed.values())]
        self.years_sheet_rows = self.get_table_rows(years_sheet_columns)
        self.city_sheet_headers = ["Город", "Уровень зарплат", " ", "Город", "Доля вакансий"]
        city_sheet_columns = [list(data.area_to_salary.keys()), list(data.area_to_salary.values()),
                           ["" for _ in data.area_to_salary.keys()], list(data.area_to_piece.keys()),
                           list(map(self.get_percents, data.area_to_piece.values()))]
        self.city_sheet_rows = self.get_table_rows(city_sheet_columns)

    @staticmethod
    def get_percents(value) -> str:
        """
        Функция для получения процентов.

        :param value: Значение которое нужно перевести в проценты
        :type value: int or float

        :return: Значение в процентах
        :rtype: str
        """
        return f"{round(value * 100, 2)}%"

    @staticmethod
    def get_table_rows(columns: list) -> list:
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
        ax.tick_params(axis='x', labelrotation=90)

    def create_horizontal_schedule(self, ax: Axes) -> None:
        """
        Функция создания горизонтальной диаграммы.

        :param ax: Глобальная позиция графика (поле для рисования)
        :type ax: Axes
        """
        ax.set_title("Уровень зарплат по городам", fontsize=16)
        ax.grid(axis="x")
        keys = [key.replace(" ", "\n").replace("-", "-\n") for key in list(self.data.area_to_salary.keys())]
        ax.barh(keys, self.data.area_to_salary.values())
        ax.tick_params(axis='y', labelsize=6)
        ax.set_yticks(keys)
        ax.set_yticklabels(labels=keys, verticalalignment="center", horizontalalignment="right")
        ax.invert_yaxis()

    def create_pie_schedule(self, ax: Axes, plt) -> None:
        """
        Функция создания круговой диаграммы.

        :param ax: Глобальная позиция графика (поле для рисования)
        :type ax: Axes

        :param plt: Общее поле для рисования всех графиков
        :type plt: Plot
        """
        ax.set_title("Доля вакансий по городам", fontsize=16)
        plt.rcParams['font.size'] = 8
        dic = self.data.area_to_piece
        dic["Другие"] = 1 - sum([val for val in dic.values()])
        keys = list(dic.keys())
        ax.pie(x=list(dic.values()), labels=keys)
        ax.axis('equal')
        ax.tick_params(axis="both", labelsize=6)
        plt.rcParams['font.size'] = 16

    def generate_schedule(self, file_name: str) -> None:
        """
        Функция создания png-файла с графиками.

        :param file_name: Название получившегося файла
        :type file_name: str
        """
        fig, axis = plt.subplots(2, 2)
        plt.rcParams['font.size'] = 8
        self.create_regular_schedule(axis[0, 0], self.data.year_to_salary.keys(), self.data.year_to_salary_needed.keys(),
                                     self.data.year_to_salary.values(), self.data.year_to_salary_needed.values(),
                          "Средняя з/п", "з/п программист", "Уровень зарплат по годам")
        self.create_regular_schedule(axis[0, 1], self.data.year_to_count.keys(), self.data.year_to_count_needed.keys(),
                                     self.data.year_to_count.values(), self.data.year_to_count_needed.values(),
                          "Количество вакансий", "Количество вакансий программист", "Количество вакансий по годам")
        self.create_horizontal_schedule(axis[1, 0])
        self.create_pie_schedule(axis[1, 1], plt)
        fig.set_size_inches(16, 9)
        fig.tight_layout(h_pad=2)
        fig.savefig(file_name)

    def generate_pdf(self, file_name: str):
        """
        Сгенерировать pdf-файл из получившихся данных, png-графиков, и HTML-шаблона с названием html_template.html.

        :param file_name: Название получившегося файла
        :type file_name: str
        """
        image_name = "graph.png"
        self.generate_schedule(image_name)
        html = open("html_template.html").read()
        template = Template(html)
        keys_to_values = {
            "prof_name": self.data.prof,
            "image_name": image_name,
            "years_headers": self.years_sheet_headers,
            "years_rows": self.years_sheet_rows,
            "cities_headers": self.city_sheet_headers,
            "count_columns": len(self.city_sheet_headers),
            "cities_rows": self.city_sheet_rows
        }
        pdf_template = template.render(keys_to_values)
        config = pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
        pdfkit.from_string(pdf_template, file_name, configuration=config, options={"enable-local-file-access": True})


def create_pdf(csv_dir: str, file_name: str) -> None:
    file_csv_name = input("Введите название файла: ")
    prof = input("Введите название профессии: ")
    data_set = DataSet(csv_dir, prof, file_csv_name)
    report = Report(data_set)
    report.generate_pdf(file_name)

if __name__ == '__main__':
    create_pdf("csv", "report_multi.pdf")