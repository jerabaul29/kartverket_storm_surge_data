import datetime
import pytz

import logging

from kartverket_stormsurge.dataset_accessor import DatasetAccessor

logging.basicConfig(level=logging.INFO)

example_kind = "full"
# example_kind = "short"

if example_kind == "full":
    start = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.utc)
    end = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc)

    start_obtain_data = datetime.datetime(2008, 1, 1, 0, 0, tzinfo=pytz.utc)
    end_obtain_data = datetime.datetime(2008, 1, 1, 1, 0, tzinfo=pytz.utc)

    path_to_nc4 = "./full_size_data_kartverket_storm_surge.nc4"
elif example_kind == "short":
    start = datetime.datetime(2008, 3, 1, 0, 0, tzinfo=pytz.utc)
    end = datetime.datetime(2008, 3, 1, 0, 0, tzinfo=pytz.utc)

    start_obtain_data = datetime.datetime(2008, 1, 1, 0, 0, tzinfo=pytz.utc)
    end_obtain_data = datetime.datetime(2008, 1, 1, 1, 0, tzinfo=pytz.utc)

    path_to_nc4 = "./small_size_data_kartverket_storm_surge.nc4"
else:
    raise ValueError("unknown example_kind")

dataset_accessor = DatasetAccessor(path_to_NetCDF=path_to_nc4)

data_out = dataset_accessor.get_data("OSL",
                                     start_obtain_data,
                                     end_obtain_data)
print("got {} by requesting data from OSL between {} and {}".format(data_out, start, end))

dataset_accessor.visualize_single_station("BGO",
                                          start_obtain_data,
                                          start_obtain_data + datetime.timedelta(days=3.0))

dataset_accessor.visualize_available_times()

print("NOTE: getting coastline and rivers may take a few seconds, be patient...")
dataset_accessor.visualize_station_positions()
