import netCDF4 as nc4
import numpy as np
import datetime
import pytz
from dataset_accessor import DatasetAccessor
import matplotlib.pyplot as plt


def generate_sub_dataset(path_to_nc4_input, path_to_nc4_output,
                         station_id,
                         datetime_start, datetime_end,
                         display=True
                         ):
    """Extract and dump as nc4 a sub-dataset for one station over
    a given time range.
    Input:
        - path_to_nc4_*: the input and output paths to nc4
        - station_id: the station to collect and dump
        - datetime_*: the start and end of the sub-dataset
        - display=True: whether to display the extracted data
    """
    dataset_accessor = DatasetAccessor(path_to_nc4_input)
    (datetimes_data, obtained_observations, obtained_predictions) = \
        dataset_accessor.get_data(station_id, datetime_start, datetime_end)

    if display:
        plt.figure()
        plt.plot(datetimes_data, obtained_observations, label="observations") 
        plt.plot(datetimes_data, obtained_predictions, label="predictions") 
        plt.ylim([-500, 500])
        plt.legend(loc="lower right")
        plt.show()

    with nc4.Dataset(path_to_nc4_output, "w", format="NETCDF4") as nc4_fh: 
        nc4_fh.set_auto_mask(False) 
        number_of_time_entries = len(datetimes_data,) 
        _ = nc4_fh.createDimension('time', number_of_time_entries) 
        timestamps = nc4_fh.createVariable('timestamps', 'i8', ('time')) 
        observations = nc4_fh.createVariable('observations', 'f4', ('time')) 
        predictions = nc4_fh.createVariable('predictions', 'f4', ('time')) 
        obtained_timestamps = [crrt_datetime.timestamp() for crrt_datetime in datetimes_data] 
        timestamps[:] = np.array(obtained_timestamps) 
        timestamps.units = "seconds since epoch" 
        observations[:] = obtained_observations 
        observations.units = "cm" 
        observations.fill_value = "1.0e37" 
        predictions[:] = obtained_predictions 
        predictions.units = "cm" 
        predictions.fill_value = "1.0e37"

path_to_nc4_input = "./full_size_data_kartverket_storm_surge.nc4"
station_id = "BGO"

# a dataset early
path_to_nc4_output = "./dataset_observations_before.nc4"
datetime_start = datetime.datetime(1991, 7, 1, 0, 0, tzinfo=pytz.utc)
datetime_end = datetime.datetime(1992, 11, 1, 0, 0, tzinfo=pytz.utc)

generate_sub_dataset(path_to_nc4_input, path_to_nc4_output,
                     station_id,
                     datetime_start, datetime_end,
                     display=True)

# a dataset in the middle
path_to_nc4_output = "./dataset_observations_middle.nc4"
datetime_start = datetime.datetime(2000, 1, 1, 0, 0, tzinfo=pytz.utc)
datetime_end = datetime.datetime(2006, 1, 1, 0, 0, tzinfo=pytz.utc)

generate_sub_dataset(path_to_nc4_input, path_to_nc4_output,
                     station_id,
                     datetime_start, datetime_end,
                     display=True)

# a dataset later
path_to_nc4_output = "./dataset_observations_after.nc4"
datetime_start = datetime.datetime(2014, 1, 1, 0, 0, tzinfo=pytz.utc)
datetime_end = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc)

generate_sub_dataset(path_to_nc4_input, path_to_nc4_output,
                     station_id,
                     datetime_start, datetime_end,
                     display=True)
