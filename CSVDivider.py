import csv
import os

class InputCorrect:
    """
    Проверка существования и заполненности файла.

    :param file: Название считываемого файла
    :type file: str
    """
    def __init__(self, file: str):
        """
        Инициализация объекта InputCorrect. Проверка на существование и заполненность файла.

        :param file: Название считываемого файла
        :type file: str
        """
        self.file_name = file
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

class DataSetDivider:
    """
    Считывание файла и формирование удобной структуры данных.

    :param input_data: Неразделенный файл и его первая строка
    :type input_data: InputCorrect

    :param csv_dir: Папка расположения CSV-файлов
    :type csv_dir: str
    """
    def __init__(self, input_data: InputCorrect, csv_dir: str):
        """
        Инициализация класса DataSet. Чтение. Разделение на разные файлы.

        :param input_data: Неразделенный файл и его первая строка
        :type input_data: InputCorrect

        :param csv_dir: Папка расположения CSV-файлов
        :type csv_dir: str
        """
        self.input_values = input_data
        self.dir = csv_dir
        self.csv_reader()
        self.csv_divide()

    def csv_reader(self) -> None:
        """
        Чтение файла и первичная фильтрация (пропуск невалидных строк).
        """
        with open(self.input_values.file_name, "r", encoding='utf-8-sig', newline='') as csv_file:
            file = csv.reader(csv_file)
            self.start_line = next(file)
            self.other_lines = [line for line in file if not ("" in line) and len(line) == len(self.start_line)]
            self.year_index = self.start_line.index("published_at")

    @staticmethod
    def get_year(date: str) -> str:
        """
        Функция вычисления года через индексы в строке.

        :param date: Дата вакансии в виде строки из csv-файла
        :type date: str

        :return: Год - 4 цифры
        :rtype: str
        """
        return date[:4]

    def save_file(self, current_year: str, lines: list) -> None:
        """
        Сохраняет CSV-файл с конкретными годами.

        :param current_year: Текущий год
        :type current_year: str

        :param lines: Список вакансий этого года
        :type lines: list
        """
        with open(f"{self.dir}/file_{current_year}.csv", "a", encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines)

    def csv_divide(self) -> None:
        """
        Разделяет данные на csv-файлы по годам.
        """
        current_year = DataSetDivider.get_year(self.other_lines[0][self.year_index])
        current_index = 0
        data_years = [[]]
        for line in self.other_lines:
            line_year = DataSetDivider.get_year(line[self.year_index])
            if line_year != current_year:
                self.save_file(current_year, data_years[current_index])
                current_year = line_year
                current_index += 1
                data_years.append([])
            data_years[current_index].append(line)
        self.save_file(current_year, data_years[current_index])

def divide_csv_file(csv_dir: str) -> DataSetDivider:
    """
    Проверяет наличие CSV-файла и разделяет его по годам на много файлов.

    :param csv_dir: Папка расположения CSV-файлов
    :type csv_dir: str

    :return: Разделение на разные файлы
    :rtype: DataSetDivider
    """
    input_data = InputCorrect(input("Введите название файла: "))
    if os.path.exists(csv_dir):
        import shutil
        shutil.rmtree(csv_dir)
    os.mkdir(csv_dir)
    data_set = DataSetDivider(input_data, csv_dir)
    return data_set


if __name__ == '__main__':
    divide_csv_file("csv")
