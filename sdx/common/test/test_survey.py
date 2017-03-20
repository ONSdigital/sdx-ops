import datetime
import unittest

from sdx.common.survey import Survey


class SurveyTests(unittest.TestCase):

    def test_datetime_ms_with_colon_in_timezone(self):
        rv = Survey.parse_timestamp("2017-01-11T17:18:53.020222+00:00")
        self.assertIsInstance(rv, datetime.datetime)

    def test_datetime_ms_with_timezone(self):
        rv = Survey.parse_timestamp("2017-01-11T17:18:53.020222+0000")
        self.assertIsInstance(rv, datetime.datetime)

    def test_datetime_zulu(self):
        rv = Survey.parse_timestamp("2017-01-11T17:18:53Z")
        self.assertIsInstance(rv, datetime.datetime)

    def test_date_iso(self):
        rv = Survey.parse_timestamp("2017-01-11")
        self.assertNotIsInstance(rv, datetime.datetime)
        self.assertIsInstance(rv, datetime.date)

    def test_date_diary(self):
        rv = Survey.parse_timestamp("11/07/2017")
        self.assertNotIsInstance(rv, datetime.datetime)
        self.assertIsInstance(rv, datetime.date)
