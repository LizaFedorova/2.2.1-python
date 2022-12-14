import pandas as pd
import sqlite3

def createSqlFromCSV(file_name: str) -> None:
    """
    Создаёт SQL-таблицу из CSV-файла
    :param file_name: Название файла относительно директории скрипта
    :return: None
    """
    df = pd.read_csv(file_name)
    conn = sqlite3.connect('currencies_db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS currencies (date text, RUR number, USD number, KZT number, BYR number,'
              'UAH number, EUR number)')
    conn.commit()
    df.to_sql('currencies', conn, if_exists='replace', index=False)

createSqlFromCSV('dataframe.csv')
