"""Tools for generating a new netCDF4 storm surge dataset."""

# TODO: add random tests on netCDF
# TODO: add class to wrap netCDF and access it

import logging
import math

import netCDF4 as nc4

import datetime
import dateutil.parser
import pytz

import numpy as np

from tqdm import tqdm

import bs4
from bs4 import BeautifulSoup as bfls

from kartverket_stormsurge.helper.url_request import NicedUrlRequest
from kartverket_stormsurge.helper.raise_assert import ras
from kartverket_stormsurge.helper.datetimes import assert_is_utc_datetime, datetime_range, datetime_segments, \
    assert_10min_multiple


def cache_organizer(request):
    """A cache organizer to be used with the NicedUrlRequest class."""

    if ("fromtime" in request) and ("totime" in request) and ("obs" in request):
        # this is a data request
        return("{}/{}/{}/".format(request[49:52], request[62:66], request[67:69]))

    elif ("stationlist" in request):
        # this is the station list request
        return("stationlist/")

    elif ("obstime" in request):
        # this is a time extent time request, i.e. metadata
        return("metadata/")
    else:
        return("")


class DatasetGenerator():
    def __init__(self, cache_folder="default"):
        """
        Input:
            - cache_folder: cache property to provide to the
                NicedUrlRequest. "default" is the user path. Can also
                provide any valid path, or None to use no caching.
        """

        self.url_requester = NicedUrlRequest(cache_folder=cache_folder,
                                             cache_organizer=cache_organizer)

        self.resolution_timedelta = datetime.timedelta(minutes=10)
        self.segment_duration = datetime.timedelta(days=5)
        self.fill_value = 1.0e37

    def get_stations_information(self):
        request = "http://api.sehavniva.no/tideapi.php?tide_request=stationlist&type=perm"
        html_string = self.url_requester.perform_request(request)
        soup = bfls(html_string, features="lxml")
        list_tags = soup.find('stationinfo').select('location')

        dict_all_stations_data = {}

        for crrt_tag in list_tags:
            dict_tag = crrt_tag.attrs
            dict_all_stations_data[dict_tag["code"]] = dict_tag

        station_ids = sorted(list(dict_all_stations_data.keys()))

        for crrt_station in station_ids:
            dict_timebouds = self.get_individual_station_time_bounds(crrt_station)
            dict_all_stations_data[crrt_station]["first_datetime"] = dict_timebouds["first"]
            dict_all_stations_data[crrt_station]["last_datetime"] = dict_timebouds["last"]

        return(dict_all_stations_data)

    def get_individual_station_time_bounds(self, station_id):
        request = "http://api.sehavniva.no/tideapi.php?tide_request=obstime&stationcode={}".format(station_id)
        html_string = self.url_requester.perform_request(request)
        soup = bfls(html_string, features="lxml")

        dict_timebounds = {}

        for crrt_time in ["first", "last"]:
            crrt_time_str = soup.select("obstime")[0][crrt_time]
            crrt_datetime = dateutil.parser.isoparse(crrt_time_str).astimezone(pytz.utc)
            dict_timebounds[crrt_time] = crrt_datetime

        return(dict_timebounds)

    def get_individual_station_data_between_datetimes(self, station_id, start, end):
        assert_is_utc_datetime(start)
        assert_is_utc_datetime(end)

        assert_10min_multiple(start)
        assert_10min_multiple(end)

        expected_datetimes = datetime_range(start, end, self.resolution_timedelta)

        expected_keys = ["prediction_cm_CD", "observation_cm_CD"]

        dict_segment = {}

        dict_bounds_station = self.get_individual_station_time_bounds(station_id)
        station_start = dict_bounds_station["first"]
        station_end = dict_bounds_station["last"]

        expect_result = False

        if self.check_time_segment_within_bounds(start, end, station_start, station_end):
            expect_result = True
            strftime_format = "%Y-%m-%dT%H:%M:%S"
            utc_time_start = start.strftime(strftime_format)
            utc_time_end = end.strftime(strftime_format)
            time_resolution_minutes = 10

            request = "https://api.sehavniva.no/tideapi.php"\
                "?stationcode={}"\
                "&fromtime={}"\
                "&totime={}"\
                "&datatype=obs"\
                "&refcode="\
                "&place="\
                "&file="\
                "&lang="\
                "&interval={}"\
                "&dst="\
                "&tzone=utc"\
                "&tide_request=stationdata".format(station_id, utc_time_start, utc_time_end, time_resolution_minutes)

            html_string = self.url_requester.perform_request(request)

            soup = bfls(html_string, features="lxml")

            for crrt_dataset in soup.findAll("data"):
                data_type = crrt_dataset["type"]
                data_unit = crrt_dataset["unit"]
                data_reflevelcode = crrt_dataset["reflevelcode"]

                crrt_key = "{}_{}_{}".format(data_type, data_unit, data_reflevelcode)

                dict_segment[crrt_key] = {}

                # individual entries are specific tags; note that the string content of each tag is empty, the data
                # is in the tag specification itself.
                for crrt_entry in crrt_dataset:
                    # effectively ignores the empty string contents, grab data from the tags
                    if type(crrt_entry) is bs4.element.Tag:
                        time = crrt_entry["time"]
                        crrt_value = float(crrt_entry["value"])
                        crrt_datetime = dateutil.parser.isoparse(time).astimezone(pytz.utc)
                        dict_segment[crrt_key][crrt_datetime] = crrt_value

        obtained_keys = list(dict_segment.keys())

        for crrt_obtained_key in obtained_keys:
            if crrt_obtained_key not in expected_keys:
                logging.warning("obtained unexpected key {}".format(crrt_obtained_key))
                del dict_segment[crrt_obtained_key]

        for crrt_expected_key in expected_keys:
            if crrt_expected_key not in obtained_keys:
                if expect_result:
                    logging.warning("missing expected key {}".format(crrt_expected_key))
                dict_segment[crrt_expected_key] = {}

        complete_dict_segment = {}

        for crrt_time in expected_datetimes:
            complete_dict_segment[crrt_time] = {}
            for crrt_dataset in expected_keys:
                if crrt_time in dict_segment[crrt_dataset]:
                    complete_dict_segment[crrt_time][crrt_dataset] = dict_segment[crrt_dataset][crrt_time]
                else:
                    complete_dict_segment[crrt_time][crrt_dataset] = self.fill_value

        return(complete_dict_segment)

    def generate_netCDF4_dataset(self, datetime_start, datetime_end, list_station_ids=None,
                                 nc4_path="./data_kartverket_storm_surge.nc4"):
        assert_is_utc_datetime(datetime_start)
        assert_is_utc_datetime(datetime_end)

        dict_station_data = self.get_stations_information()
        list_available_station_ids = sorted(list(dict_station_data.keys()))

        if list_station_ids is None:
            list_station_ids = list_available_station_ids
        else:
            for crrt_station in list_station_ids:
                ras(crrt_station in list_available_station_ids)

        ras(isinstance(list_station_ids, list))

        timestamps_vector = [crrt_datetime.timestamp() for
                             crrt_datetime in datetime_range(datetime_start,
                                                             datetime_end,
                                                             self.resolution_timedelta)]

        number_of_time_entries = len(timestamps_vector)

        with nc4.Dataset(nc4_path, "w", format="NETCDF4") as nc4_fh:
            nc4_fh.set_auto_mask(False)

            description_string = "Storm surge dataset from the Norwegian coast,"\
                                 "built from the data obtained from kartverket web API,"\
                                 "using the code at:"\
                                 "MachineOcean-WP12/storm_surge/learn_error/prepare_data/prepare_data.py"

            nc4_fh.Conventions = "CF-X.X"
            nc4_fh.title = "storm surge from kartverket API"
            nc4_fh.description = description_string
            nc4_fh.institution = "IT department, Norwegian Meteorological Institute"
            nc4_fh.Contact = "jeanr@met.no"

            _ = nc4_fh.createDimension('station', len(list_station_ids))
            _ = nc4_fh.createDimension('time', number_of_time_entries)

            stationid = nc4_fh.createVariable("stationid", str, ('station'))
            latitude = nc4_fh.createVariable('latitude', 'f4', ('station'))
            longitude = nc4_fh.createVariable('longitude', 'f4', ('station'))
            timestamps = nc4_fh.createVariable('timestamps', 'i8', ('time'))
            observation = nc4_fh.createVariable('observation', 'f4', ('station', 'time'))
            prediction = nc4_fh.createVariable('prediction', 'f4', ('station', 'time'))
            timestamp_start = nc4_fh.createVariable('timestamp_start', 'i8', ('station'))
            timestamp_end = nc4_fh.createVariable('timestamp_end', 'i8', ('station'))

            # TODO: add more metadata details

            timestamps[:] = timestamps_vector

            for ind, crrt_station_id in tqdm(enumerate(list_station_ids),
                                             desc="station", total=len(list_station_ids)):
                stationid[ind] = crrt_station_id
                latitude[ind] = dict_station_data[crrt_station_id]["latitude"]
                longitude[ind] = dict_station_data[crrt_station_id]["longitude"]

                dict_crrt_timebounds = self.get_individual_station_time_bounds(crrt_station_id)
                timestamp_start[ind] = dict_crrt_timebounds["first"].timestamp()
                timestamp_end[ind] = dict_crrt_timebounds["last"].timestamp()

                np_observations = -self.fill_value * np.ones((number_of_time_entries,))
                np_predictions = -self.fill_value * np.ones((number_of_time_entries,))

                crrt_filling_index = 0
                approx_nbr_segments = math.ceil((datetime_end - datetime_start) / self.segment_duration)

                for crrt_segment in tqdm(datetime_segments(datetime_start,
                                                           datetime_end,
                                                           self.segment_duration
                                                           ),
                                         desc="segment", total=approx_nbr_segments
                                         ):

                    dict_crrt_segment =\
                        self.get_individual_station_data_between_datetimes(crrt_station_id,
                                                                           crrt_segment[0],
                                                                           crrt_segment[1])

                    for crrt_time in list(dict_crrt_segment.keys()):
                        ras(timestamps[crrt_filling_index] == crrt_time.timestamp())
                        np_observations[crrt_filling_index] = dict_crrt_segment[crrt_time]["observation_cm_CD"]
                        np_predictions[crrt_filling_index] = dict_crrt_segment[crrt_time]["prediction_cm_CD"]
                        crrt_filling_index += 1

                observation[ind, :] = np_observations
                prediction[ind, :] = np_predictions

        # populate metadata
        # note: initialize the whole dataset as "invalid"
        pass

    def check_time_segment_within_bounds(self, segment_start, segment_end, bound_start, bound_end):
        assert_is_utc_datetime(segment_start)
        assert_is_utc_datetime(segment_end)
        assert_is_utc_datetime(bound_start)
        assert_is_utc_datetime(bound_end)

        ras(segment_start < segment_end)
        ras(bound_start < bound_end)

        if (segment_start > bound_start) and (segment_end < bound_end):
            return(True)
        else:
            return(False)
