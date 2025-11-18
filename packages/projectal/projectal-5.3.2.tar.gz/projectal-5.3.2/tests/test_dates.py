import projectal

from tests.base_test import BaseTest


class TestDates(BaseTest):
    def test_convert(self):
        date = "2022-03-18"
        ts = 1647561600000
        assert projectal.timestamp_from_date(date) == ts
        assert projectal.date_from_timestamp(ts) == date
        assert projectal.timestamp_from_date(None) is None
        assert projectal.date_from_timestamp(None) is None
