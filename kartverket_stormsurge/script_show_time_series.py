
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

list_stations = list(dataset_accessor.station_ids)
print(list_stations)

for crrt_station in [list_stations[23]]:
    print("show {}".format(crrt_station))
    dataset_accessor.visualize_single_station(crrt_station,
                                              start,
                                              end)
