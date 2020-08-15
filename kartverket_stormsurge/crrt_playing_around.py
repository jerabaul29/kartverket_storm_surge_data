import datetime
import pytz

import netCDF4 as nc4

from kartverket_stormsurge.dataset_generator import DatasetGenerator
import pprint

pp = pprint.PrettyPrinter(indent=2).pprint

dataset_generator = DatasetGenerator()

dict_stations_information = dataset_generator.get_stations_information()
pp(dict_stations_information)

dict_individual_time_bounds = dataset_generator.get_individual_station_time_bounds("VIK")
pp(dict_individual_time_bounds)

start = datetime.datetime(2000, 10, 16, 16, 30, tzinfo=pytz.utc)
end = datetime.datetime(2000, 10, 16, 17, 30, tzinfo=pytz.utc)
station_id = "VIK"
dict_dataset_segment = dataset_generator.get_individual_station_data_between_datetimes(station_id, start, end)
pp(dict_dataset_segment)

start = datetime.datetime(2000, 10, 16, 16, 30, tzinfo=pytz.utc)
end = datetime.datetime(2000, 11, 16, 17, 30, tzinfo=pytz.utc)
dataset_generator.generate_netCDF4_dataset(start, end, list_station_ids=["VIK"])

dataset_generator.generate_netCDF4_dataset(start, end, list_station_ids=["VIK", "OSL", "RVK"])

path_to_nc4 = "./data_kartverket_storm_surge.nc4"

nc4_fh = nc4.Dataset(path_to_nc4)

print(nc4_fh)

nc4_fh["stationid"][:]
