import datetime
import pytz

from kartverket_stormsurge.dataset_generator import DatasetGenerator
from kartverket_stormsurge.dataset_accessor import DatasetAccessor

dataset_generator = DatasetGenerator()

start = datetime.datetime(2000, 10, 16, 16, 30, tzinfo=pytz.utc)
end = datetime.datetime(2000, 10, 16, 17, 30, tzinfo=pytz.utc)

start = datetime.datetime(2000, 10, 16, 16, 30, tzinfo=pytz.utc)
end = datetime.datetime(2000, 11, 16, 17, 30, tzinfo=pytz.utc)

dataset_generator.generate_netCDF4_dataset(start, end)

dataset_accessor = DatasetAccessor()

dataset_accessor.visualize_available_times()
dataset_accessor.visualize_station_positions()
