import datetime
import pytz

from kartverket_stormsurge.helper.datetimes import datetime_range
from kartverket_stormsurge.helper.last_thursday_of_the_month import get_last_thursday_in_month


def test_1():
    datetime_start = datetime.datetime(2020, 8, 1, 0, 0, tzinfo=pytz.utc)
    datetime_end = datetime.datetime(2020, 9, 1, 0, 0, tzinfo=pytz.utc)
    last_thrusday = datetime.datetime(2020, 8, 27, 0, 0, tzinfo=pytz.utc)

    for crrt_day in datetime_range(datetime_start, datetime_end, datetime.timedelta(days=1)):
        assert get_last_thursday_in_month(crrt_day) == last_thrusday 


def test_2():
    datetime_start = datetime.datetime(2020, 9, 1, 0, 0, tzinfo=pytz.utc)
    datetime_end = datetime.datetime(2020, 10, 1, 0, 0, tzinfo=pytz.utc)
    last_thrusday = datetime.datetime(2020, 9, 24, 0, 0, tzinfo=pytz.utc)

    for crrt_day in datetime_range(datetime_start, datetime_end, datetime.timedelta(days=1)):
        assert get_last_thursday_in_month(crrt_day) == last_thrusday 


def test_3():
    datetime_start = datetime.datetime(2020, 12, 1, 0, 0, tzinfo=pytz.utc)
    datetime_end = datetime.datetime(2021, 1, 1, 0, 0, tzinfo=pytz.utc)
    last_thrusday = datetime.datetime(2020, 12, 31, 0, 0, tzinfo=pytz.utc)

    for crrt_day in datetime_range(datetime_start, datetime_end, datetime.timedelta(days=1)):
        assert get_last_thursday_in_month(crrt_day) == last_thrusday 
