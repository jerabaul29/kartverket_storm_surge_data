"""Tools for generating a new netCDF4 storm surge dataset."""

# TODO: add random tests on netCDF
# TODO: add class to wrap netCDF and access it

import logging

import datetime
import pytz

import bs4
from bs4 import BeautifulSoup as bfls

from kartverket_stormsurge.helper.url_request import NicedUrlRequest
from kartverket_stormsurge.helper.raise_assert import ras
from kartverket_stormsurge.helper.datetimes import assert_is_utc


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
            crrt_datetime = datetime.datetime.fromisoformat(crrt_time_str).astimezone(pytz.utc)
            dict_timebounds[crrt_time] = crrt_datetime

        return(dict_timebounds)

    def get_individual_station_data_between_datetimes(self, station_id, start, end):
        # TODO: assert time is multiple of 10 minutes

        ras(isinstance(start, datetime.datetime))
        ras(isinstance(end, datetime.datetime))

        assert_is_utc(start)
        assert_is_utc(end)

        expected_keys = ["prediction_cm_CD", "observation_cm_CD"]

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

        print(request)
        html_string = self.url_requester.perform_request(request)

        print(html_string)
        soup = bfls(html_string, features="lxml")

        dict_segment = {}

        for crrt_dataset in soup.findAll("data"):
            data_type = crrt_dataset["type"]
            data_unit = crrt_dataset["unit"]
            data_reflevelcode = crrt_dataset["reflevelcode"]

            crrt_key = "{}_{}_{}".format(data_type, data_unit, data_reflevelcode)

            dict_segment[crrt_key] = []

            # individual entries are specific tags; note that the string content of each tag is empty, the data
            # is in the tag specification itself.
            for crrt_entry in crrt_dataset:
                # effectively ignores the empty string contents, grab data from the tags
                if type(crrt_entry) is bs4.element.Tag:
                    time = crrt_entry["time"]
                    value = float(crrt_entry["value"])
                    data_tuple = (datetime.datetime.fromisoformat(time), value)
                    dict_segment[crrt_key].append(data_tuple)

        obtained_keys = list(dict_segment.keys())

        for crrt_obtained_key in obtained_keys:
            if crrt_obtained_key not in expected_keys:
                logging.warning("obtained unexpected key {}".format(crrt_obtained_key))

        for crrt_expected_key in expected_keys:
            if crrt_expected_key not in obtained_keys:
                logging.warning("missing expected key {}".format(crrt_expected_key))

        return(dict_segment)

    def generate_netCDF4_dataset(self, datetime_start, datetime_end, list_stations=None):
        # populate metadata
        # for each station: split time into segments, check if should request, fill with available data
        # note: initialize the whole dataset as "invalid"
        # TODO: assert time is a multiple of 10 mintues
        pass

    def check_time_segment_within_bounds(self, segment_start, segment_end, bound_start, bound_end):
        # check if within bounds before doing a request
        pass
