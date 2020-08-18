import datetime
import pytz

import logging

from kartverket_stormsurge.dataset_checker import DatasetChecker

logging.basicConfig(level=logging.INFO)

example_kind = "full"
# example_kind = "short"

if example_kind == "full":
    start = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.utc)
    end = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc)

    path_to_nc4 = "./full_size_data_kartverket_storm_surge.nc4"
elif example_kind == "short":
    start = datetime.datetime(2008, 1, 1, 0, 0, tzinfo=pytz.utc)
    end = datetime.datetime(2008, 6, 1, 0, 0, tzinfo=pytz.utc)

    path_to_nc4 = "./small_size_data_kartverket_storm_surge.nc4"
else:
    raise ValueError("unknown example_kind")

dataset_checker = DatasetChecker(path_to_ordered_cache="/home/jrlab/.NicedUrlRequest/cache/",
                                 path_to_netCDF=path_to_nc4,
                                 limit_datetimes=(start, end))

dataset_checker.perform_random_tests(10000)
