import datetime
import pytz

from kartverket_stormsurge.helper.raise_assert import ras

def assert_is_utc_datetime(date_in):
    ras(isinstance(date_in, datetime.datetime))

    if not date_in.tzinfo == pytz.utc:
        raise Exception("not utc!")


def datetime_range(datetime_start, datetime_end, step_timedelta):
    assert_is_utc_datetime(datetime_start)
    assert_is_utc_datetime(datetime_end)
    ras(isinstance(step_timedelta, datetime.timedelta))
    ras(datetime_start < datetime_end)
    ras(step_timedelta > datetime.timedelta(0))

    crrt_time = datetime_start
    yield crrt_time

    while True:
        crrt_time += step_timedelta
        if crrt_time < datetime_end:
            yield crrt_time
        else:
            break


def datetime_segments(datetime_start, datetime_end, step_timedelta):
    assert_is_utc_datetime(datetime_start)
    assert_is_utc_datetime(datetime_end)
    ras(isinstance(step_timedelta, datetime.timedelta))
    ras(datetime_start < datetime_end)
    ras(step_timedelta > datetime.timedelta(0))

    crrt_segment_start = datetime_start
    crrt_segment_end = crrt_segment_start + step_timedelta

    while True:
        if crrt_segment_end >= datetime_end:
            yield (crrt_segment_start, datetime_end)
            break
        else:
            yield (crrt_segment_start, crrt_segment_end)
            crrt_segment_start += step_timedelta
            crrt_segment_end += step_timedelta
