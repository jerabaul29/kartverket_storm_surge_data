import datetime
import pytz

from kartverket_stormsurge.helper.datetimes import assert_is_utc_datetime

def get_last_thursday_in_month(datetime_in):
    assert_is_utc_datetime(datetime_in)

    thursday_index = 3

    crrt_month = datetime_in.month
    crrt_year = datetime_in.year

    crrt_day = datetime.datetime(crrt_year, crrt_month, 1, 0, 0, tzinfo=pytz.utc)
    last_thursday = None

    while True:
        if crrt_day.month != crrt_month:
            break
        elif crrt_day.weekday() == thursday_index:
            last_thursday = crrt_day 

        crrt_day += datetime.timedelta(days=1)

    return(last_thursday)
