import os

import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import cartopy.crs as ccrs
import cartopy.feature as cfeature

import netCDF4 as nc4

from kartverket_stormsurge.helper.raise_assert import ras
from kartverket_stormsurge.helper.datetimes import assert_is_utc_datetime

from kartverket_stormsurge.helper.arrays import find_index_first_greater_or_equal


class DatasetAccessor():
    def __init__(self, path_to_NetCDF=None):
        if path_to_NetCDF is None:
            self.path_to_NetCDF = os.getcwd() + "/data_kartverket_storm_surge.nc4"
        else:
            self.path_to_NetCDF = path_to_NetCDF

        self.explore_information()

    def explore_information(self):
        with nc4.Dataset(self.path_to_NetCDF, "r", format="NETCDF4") as nc4_fh:
            self.station_ids = nc4_fh["stationid"][:]
            self.number_of_stations = len(self.station_ids)
            self.first_timestamp = int(nc4_fh["timestamps"][0])
            self.last_timestamp = int(nc4_fh["timestamps"][-1])

        self.dict_metadata = self.get_dict_stations_metadata()

    def get_dict_stations_metadata(self):
        dict_stations_metadata = {}

        with nc4.Dataset(self.path_to_NetCDF, "r", format="NETCDF4") as nc4_fh:
            for crrt_ind in range(self.number_of_stations):
                crrt_station_id = nc4_fh["stationid"][crrt_ind]
                crrt_lat = nc4_fh["latitude"][crrt_ind]
                crrt_lon = nc4_fh["longitude"][crrt_ind]
                datetime_start = datetime.datetime.fromtimestamp((nc4_fh["timestamp_start"][crrt_ind].data))
                datetime_end = datetime.datetime.fromtimestamp((nc4_fh["timestamp_end"][crrt_ind].data))

                crrt_dict_metadata = {}
                crrt_dict_metadata["station_index"] = crrt_ind
                crrt_dict_metadata["nc4_dump_index"] = crrt_ind
                crrt_dict_metadata["latitude"] = crrt_lat
                crrt_dict_metadata["longitude"] = crrt_lon
                crrt_dict_metadata["datetime_start"] = datetime_start
                crrt_dict_metadata["datetime_end"] = datetime_end

                dict_stations_metadata[crrt_station_id] = crrt_dict_metadata

        return dict_stations_metadata

    def visualize_available_times(self, date_start=None, date_end=None):
        """Visualize the time over which data are available for each station.
        This is based on the specific API request about data availability.
        Inputs:
            - date_start, date_end: dates over which we want to check if data
                are available. If None (default), ignore time bounds for the
                and do no availability check.
        Output:
            Displays a plot showing the stations, the time extent over which
                data are available, and, if provided, the time bounds date_start
                and date_end."""

        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(18, 5))

        for crrt_station_id in self.station_ids:
            crrt_station_index = self.dict_metadata[crrt_station_id]["station_index"]

            if crrt_station_index % 2 == 0:
                crrt_color = "b"
            else:
                crrt_color = 'k'

            crrt_min_time = self.dict_metadata[crrt_station_id]["datetime_start"]
            crrt_max_time = self.dict_metadata[crrt_station_id]["datetime_end"]

            plt.plot([crrt_min_time, crrt_max_time], [crrt_station_index, crrt_station_index],
                     linewidth=3.5, color=crrt_color)

            plt.text(datetime.datetime(1980, 1, 1), crrt_station_index,
                     "#{:02}{} {}.{:02}-{}.{:02}".format(crrt_station_index,
                                                         crrt_station_id,
                                                         crrt_min_time.year,
                                                         crrt_min_time.month,
                                                         crrt_max_time.year,
                                                         crrt_max_time.month),
                     color=crrt_color)

            if date_start is not None and date_end is not None:
                if (date_start > crrt_min_time and date_end < crrt_max_time):
                    plt.text(datetime.datetime(1985, 6, 1), crrt_station_index, "Y", color="g")
                else:
                    plt.text(datetime.datetime(1985, 6, 1), crrt_station_index, "N", color="r")

        if date_start is not None and date_end is not None:
            plt.axvline(date_start, linewidth=2.5, color="orange")
            plt.axvline(date_end, linewidth=2.5, color="orange")

        mpl_min_time = mdates.date2num(datetime.datetime(1980, 1, 1))
        mpl_max_time = mdates.date2num(datetime.datetime(2020, 12, 1))

        plt.xlim([mpl_min_time, mpl_max_time])
        plt.ylabel("station number")

        plt.show()

    def visualize_station_positions(self):
        """Visualize the position of the stations."""

        # The data to plot are defined in lat/lon coordinate system, so PlateCarree()
        # is the appropriate choice of coordinate reference system:
        _ = ccrs.PlateCarree()

        # the map projection properties.
        proj = ccrs.LambertConformal(central_latitude=65.0,
                                     central_longitude=15.0,
                                     standard_parallels=(52.5, 75.0))

        plt.figure(figsize=(15, 18))
        ax = plt.axes(projection=proj)

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.LAKES)
        ax.add_feature(cfeature.RIVERS)
        ax.set_global()
        ax.coastlines()

        list_lats = []
        list_lons = []
        list_names = []

        for crrt_station_id in self.station_ids:
            list_lats.append(self.dict_metadata[crrt_station_id]["latitude"])
            list_lons.append(self.dict_metadata[crrt_station_id]["longitude"])
            list_names.append(crrt_station_id)

        ax.scatter(list_lons, list_lats, transform=ccrs.PlateCarree(), color="red")

        transform = ccrs.PlateCarree()._as_mpl_transform(ax)
        for crrt_station_index in range(self.number_of_stations):
            ax.annotate("#{}{}".format(crrt_station_index, list_names[crrt_station_index]),
                        xy=(list_lons[crrt_station_index], list_lats[crrt_station_index]),
                        xycoords=transform,
                        xytext=(5, 5), textcoords="offset points", color="red"
                        )

        ax.set_extent([-3.5, 32.5, 50.5, 82.5])

        plt.show()

    def visualize_single_station(self, station_id, datetime_start, datetime_end):
        """Show the data for both observation and prediction for a specific station over
        a specific time interval.
        Input:
            - station_id: the station to look at
            - datetime_start: the start of the plot
            - datetime_end: the end of the plot
        """

        timestamps, observation, prediction = self.get_data(station_id, datetime_start, datetime_end)
        datetime_timestamps = [datetime.datetime.fromtimestamp(crrt_datetime) for crrt_datetime in timestamps]

        plt.figure()

        plt.plot(datetime_timestamps, observation)
        plt.plot(datetime_timestamps, prediction)

        plt.ylim([-1000.0, 1000.0])

        plt.show()

    def get_data(self, station_id, datetime_start, datetime_end):
        """Get the data contained in the netcdf4 dump about stations_id, that
        is between times datetime_start and datetime_end.
        Input:
            - sation_id: the station ID, for example 'OSL'
            - datetime_start, datetime_end: the limits of the extracted data.
        Output:
            - data_timestamps: the timestamps of the data.
            - data_observation: the observation.
            - data_prediction: the prediction.
        """

        ras(station_id in self.station_ids)
        assert_is_utc_datetime(datetime_start)
        assert_is_utc_datetime(datetime_end)
        ras(datetime_start < datetime_end)
        ras(datetime_start > datetime.datetime.fromtimestamp(self.first_timestamp))
        ras(datetime_end < datetime.datetime.fromtimestamp(self.last_timestamp))

        nc4_index = self.dict_metadata[station_id]["station_index"]

        timestamp_start = datetime_start.timestamp()
        timestamp_end = datetime_end.timestamp()

        with nc4.Dataset(self.path_to_NetCDF, "r", format="NETCDF4") as nc4_fh:
            data_timestamp_full = nc4_fh["timestamps"][:]
            data_observation_full = nc4_fh["observation"][nc4_index][:]
            data_prediction_full = nc4_fh["prediction"][nc4_index][:]

        first_index = find_index_first_greater_or_equal(data_timestamp_full, timestamp_start)
        last_index = find_index_first_greater_or_equal(data_timestamp_full, timestamp_end) + 1

        data_timestamp = data_timestamp_full[first_index:last_index]
        data_observation = data_observation_full[first_index:last_index]
        data_prediction = data_prediction_full[first_index:last_index]

        return(data_timestamp, data_observation, data_prediction)
