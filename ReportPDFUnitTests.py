from unittest import TestCase
from ReportPDF import *

class ReportPDFUnitTests(TestCase):
    def test_get_percents_from_zero(self):
        self.assertEqual(Report.get_percents(0), "0%")

    def test_get_percents_from_one(self):
        self.assertEqual(Report.get_percents(1), "100%")

    def test_get_percents_from_half(self):
        self.assertEqual(Report.get_percents(0.5), "50.0%")

    def test_get_percents_with_float_percents(self):
        self.assertEqual(Report.get_percents(0.753), '75.3%')

    def test_get_percents_with_super_float_percents(self):
        self.assertEqual(Report.get_percents(0.7001), '70.01%')

    def test_get_percents_with_round_super_float_percents(self):
        self.assertEqual(Report.get_percents(0.70015), '70.02%')

    def test_get_table_rows_with_table_from_one_elem(self):
        self.assertEqual(Report.get_table_rows([[1]]), [[1]])

    def test_get_table_rows_with_2_x_2(self):
        self.assertEqual(Report.get_table_rows([[1, 1], [2, 2]]), [[1, 2], [1, 2]])

    def test_get_table_rows_with_3_x_3(self):
        self.assertEqual(Report.get_table_rows([[1, 2, 3], [1, 2, 3], [1, 2, 3]]), [[1, 1, 1], [2, 2, 2], [3, 3, 3]])

    def test_get_table_rows_with_3_x_3_with_number_in_the_corner(self):
        self.assertEqual(Report.get_table_rows([[1, 2, 3], [1, 2, 3], [1, 2, 10]]), [[1, 1, 1], [2, 2, 2], [3, 3, 10]])

    def test_get_data(self):
        self.assertEqual(get_data('2022-05-31T17:32:49+0300'), 2022)

    def test_float_salary_from_in_to_rub(self):
        self.assertEqual(Salary(10.0, 20, 'RUR').to_rub(10.0 + 20), 30.0)

    def test_float_salary_to_in_to_rub(self):
        self.assertEqual(Salary(10, 20.0, 'RUR').to_rub(10 + 20.0), 30.0)

    def test_EUR_currency_in_to_rub(self):
        self.assertEqual(Salary(10, 20, 'EUR').to_rub(10 + 20), 1797.0)

    def test_AZN_currency_in_to_rub(self):
        self.assertEqual(Salary(10, 20, 'AZN').to_rub(10 + 20), 1070.4)

    def test_clean_html_and_spaces_simple(self):
        self.assertEqual(DataSet.delete_html("abc"), "abc")

    def test_clean_html_and_spaces_with_double_tag(self):
        self.assertEqual(DataSet.delete_html("<div>abc</div>"), 'abc')

    def test_clean_html_and_spaces_with_one_tag(self):
        self.assertEqual(DataSet.delete_html("<div>abc"), 'abc')

    def test_clean_html_and_spaces_with_spaces(self):
        self.assertEqual(DataSet.delete_html("   abc  "), "abc")

    def test_clean_html_and_spaces_with_spaces_and_two_words(self):
        self.assertEqual(DataSet.delete_html(" abc     abd"), 'abc abd')

    def test_clean_html_and_spaces_with_many_spaces_and_tags(self):
        self.assertEqual(DataSet.delete_html(" <div><strong><i>  abc <i>  abd  <string>"), 'abc abd')

    def test_clean_html_and_spaces_with_many_spaces_and_tags_and_incorrect_tag(self):
        self.assertEqual(DataSet.delete_html(" <div> abc <iqewqljl> <  div   > abd <i>"), 'abc abd')
