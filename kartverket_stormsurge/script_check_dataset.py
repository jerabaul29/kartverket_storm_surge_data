import datetime
import pytz

from kartverket_stormsurge.dataset_checker import DatasetChecker

start = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.utc)
end = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc)

path_to_nc4 = "./full_size_data_kartverket_storm_surge.nc4"
datetime_checker = DatasetChecker(path_to_ordered_cache="default", path_to_netCDF=path_to_nc4,
                                  limit_datetimes=(start, end))

datetime_checker.perform_random_tests(10000)
