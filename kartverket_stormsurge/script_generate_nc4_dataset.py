import datetime
import pytz

from kartverket_stormsurge.dataset_generator import DatasetGenerator

dataset_generator = DatasetGenerator()

# example_kind = "full"
example_kind = "short"

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

start = datetime.datetime(2008, 1, 1, 0, 0, tzinfo=pytz.utc)
end = datetime.datetime(2008, 6, 1, 0, 0, tzinfo=pytz.utc)

path_to_nc4 = "./small_size_data_kartverket_storm_surge.nc4"

dataset_generator.generate_netCDF4_dataset(start, end, nc4_path=path_to_nc4)
