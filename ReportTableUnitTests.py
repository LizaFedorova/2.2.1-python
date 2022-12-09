from unittest import TestCase
from ReportTable import *


class ReportTableUnitTests(TestCase):
    def test_salary_from(self):
        self.assertEqual(Salary(10.0, 20.4, True, 'RUR').salary_from, 10.0)

    def test_salary_to(self):
        self.assertEqual(Salary(10.0, 20.4, True, 'RUR').salary_to, 20.4)

    def test_salary_gross(self):
        self.assertEqual(Salary(10.0, 20.4, True, 'RUR').salary_gross, True)

    def test_salary_currency(self):
        self.assertEqual(Salary(10.0, 20.4, True, 'RUR').salary_currency, 'RUR')

    def test_float_salary_from_in_to_rub(self):
        self.assertEqual(Salary(10.0, 20, True, 'RUR').to_rub(10.0 + 20), 30.0)

    def test_float_salary_to_in_to_rub(self):
        self.assertEqual(Salary(10, 20.0, True, 'RUR').to_rub(10 + 20.0), 30.0)

    def test_currency_in_to_rub(self):
        self.assertEqual(Salary(10, 20, True, 'EUR').to_rub(10 + 20), 1797.0)

    def test_AZN_currency_in_to_rub(self):
        self.assertEqual(Salary(10, 20, True, 'AZN').to_rub(10 + 20), 1070.4)

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

    def test_data(self):
        self.assertEqual(get_data('2022-05-31T17:32:49+0300'), '31.05.2022')

