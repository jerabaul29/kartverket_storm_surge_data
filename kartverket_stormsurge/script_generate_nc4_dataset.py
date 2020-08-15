import datetime
import pytz

from kartverket_stormsurge.dataset_generator import DatasetGenerator

dataset_generator = DatasetGenerator()

start = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.utc)
end = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc)

path_to_nc4 = "./full_size_data_kartverket_storm_surge.nc4"
dataset_generator.generate_netCDF4_dataset(start, end, nc4_path=path_to_nc4)
