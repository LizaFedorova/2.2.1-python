import ReportTable
import ReportPDF

def main():
    """Выбор формирования отчета: в виде pdf или таблицы PrettyTable."""
    type_of_report = input("Введите тип отчета (Вакансии/Статистика): ")

    if type_of_report == "Вакансии":
        ReportTable.create_table()

    elif type_of_report == "Статистика":
        ReportPDF.create_report()

    else:
        print("Неверный тип отчета!")
        exit()

main()
