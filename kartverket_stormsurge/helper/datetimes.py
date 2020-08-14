import datetime
import pytz

from kartverket_stormsurge.helper.raise_assert import ras

def assert_is_utc(date_in):
    ras(isinstance(date_in, datetime.datetime))

    if not date_in.tzinfo == pytz.utc:
        raise Exception("not utc!")
