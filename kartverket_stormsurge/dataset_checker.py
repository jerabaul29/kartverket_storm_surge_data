import os
from pathlib import Path
import random

import bs4
from bs4 import BeautifulSoup as bfls
import logging

import datetime
import dateutil.parser
import pytz

from tqdm import tqdm

from kartverket_stormsurge.dataset_accessor import DatasetAccessor
from kartverket_stormsurge.helper.datetimes import assert_is_utc_datetime


class DatasetChecker():
    """A class to perform checks of the correctness of the netCDF data dump a posteriori."""

    def __init__(self, path_to_ordered_cache, path_to_netCDF, limit_datetimes):
        """
        Input:
            - path_to_ordered_cache: the path to the ordered cache with the html requests that
                were used to build the netCDF database. For example: /home/jrmet/.NicedUrlRequest/cache/
            - path_to_netCDF: the path to the netCDF database.
            - limit_dates: the limit dates over which testing is allowed.
        """

        self.path_to_ordered_cache = path_to_ordered_cache
        self.path_to_netCDF = path_to_netCDF
        self.limit_datetimes = limit_datetimes

        assert_is_utc_datetime(limit_datetimes[0])
        assert_is_utc_datetime(limit_datetimes[1])

        if not os.path.exists(self.path_to_ordered_cache):
            raise ValueError("path to ordered cache {} does not exist".format(self.path_to_ordered_cache))

        if not self.path_to_ordered_cache[-1] == "/":
            raise ValueError("please terminate path_to_ordered_cache with /")

        if not Path(self.path_to_netCDF).is_file():
            raise ValueError("path to netCDF dump {} does not exist".format(self.path_to_netCDF))

        self.kartverket_nc4 = DatasetAccessor(self.path_to_netCDF)

    def perform_random_tests(self, n_tests=1000):
        """
        Input:
            - n_tests: the number of tests to perform at random.
        """

        list_data_folders = [x[0] for
                             x in os.walk(self.path_to_ordered_cache)
                             if len(x[0]) == 11 + len(self.path_to_ordered_cache)]

        for test_index in tqdm(range(n_tests)):
            crrt_folder = random.choice(list_data_folders)
            crrt_station = crrt_folder[-11:-8]

            logging.info(crrt_station)

            list_files = os.listdir(crrt_folder)
            crrt_path = "{}/{}".format(crrt_folder, random.choice(list_files))

            iso_to_parse = crrt_path[-139:-120]
            print("iso to parse: {}".format(iso_to_parse))

            if len(iso_to_parse) == 19 and iso_to_parse[4] == "-" and iso_to_parse[7] == "-" and iso_to_parse[10] == "T":
                crrt_start_datetime_pathname = dateutil.parser.isoparse(iso_to_parse).astimezone(pytz.utc)
                logging.info(crrt_start_datetime_pathname)

                # parse the current file
                with open(crrt_path, 'rb') as fh:
                    html_string = fh.read()
                soup = bfls(html_string, features="lxml")

                dict_segment = {}

                # each segment has several datasets
                for crrt_dataset in soup.findAll("data"):
                    data_type = crrt_dataset["type"]
                    data_unit = crrt_dataset["unit"]
                    data_reflevelcode = crrt_dataset["reflevelcode"]

                    crrt_key = "{}_{}_{}".format(data_type, data_unit, data_reflevelcode)

                    if crrt_key not in dict_segment:
                        logging.info("create entry {} in the current station data dict".format(crrt_key))
                        dict_segment[crrt_key] = []

                    # individual entries are specific tags; note that the string content of each tag is empty, the data
                    # is in the tag specification itself.
                    for crrt_entry in crrt_dataset:
                        # effectively ignores the empty string contents, grab data from the tags
                        if type(crrt_entry) is bs4.element.Tag:
                            time = crrt_entry["time"]
                            value = float(crrt_entry["value"])
                            data_tuple = (dateutil.parser.isoparse(time).astimezone(pytz.utc), value)
                            dict_segment[crrt_key].append(data_tuple)

                if list(dict_segment.keys()) != []:
                    crrt_key = random.choice(list(dict_segment.keys()))

                    crrt_data_tuple = random.choice(dict_segment[crrt_key])

                    crrt_datetime = crrt_data_tuple[0]

                    if crrt_datetime.replace(tzinfo=pytz.utc) > self.limit_datetimes[0]\
                            and crrt_datetime.replace(tzinfo=pytz.utc) < self.limit_datetimes[1]:

                        crrt_data = crrt_data_tuple[1]

                        logging.info("chose crrt tuple {} with key {} from station {} from file {}"
                                     .format(crrt_data_tuple, crrt_key, crrt_station, crrt_path))
                        logging.info("corresponding to datetime: {}".format(crrt_datetime))

                        datetime_start_data = crrt_datetime.replace(tzinfo=pytz.utc)
                        datetime_end_data = (crrt_datetime + datetime.timedelta(minutes=1)).replace(tzinfo=pytz.utc)

                        datetimes, observation, prediction =\
                            self.kartverket_nc4.get_data(crrt_station, datetime_start_data, datetime_end_data)

                        datetimes_nc4 = datetimes[0]
                        observation_nc4 = observation[0]
                        prediction_nc4 = prediction[0]

                        logging.info("the netcdf4 datafile provided station {} timestamp {} observation {} prediction {}:"
                                     .format(crrt_station, datetimes_nc4, observation_nc4, prediction_nc4))

                        assert datetimes_nc4 == crrt_datetime

                        if "observation" in crrt_key:
                            logging.info("compare obs {} from request to {} from nc4".format(crrt_data, observation_nc4))
                            assert abs(observation_nc4 - crrt_data) < 1e-2
                        elif "prediction" in crrt_key:
                            logging.info("compare pred {} from request to {} from nc4".format(crrt_data, prediction_nc4))
                            logging.info(prediction_nc4)
                            logging.info(crrt_data)
                            assert abs(prediction_nc4 - crrt_data) < 1e-2
                        else:
                            raise ValueError("unknown key {}".format(crrt_key))

                    else:
                        logging.warning("skipping test with datetime {} outside range".format(crrt_datetime))
                else:
                    datetime_start_data = crrt_start_datetime_pathname.replace(tzinfo=pytz.utc)
                    datetime_end_data = (datetime_start_data + datetime.timedelta(minutes=1)).replace(tzinfo=pytz.utc)

                    if datetime_start_data > self.limit_datetimes[0] and datetime_start_data < self.limit_datetimes[1]:

                        datetimes, observation, prediction =\
                            self.kartverket_nc4.get_data(crrt_station, datetime_start_data, datetime_end_data)

                        datetimes_nc4 = datetimes[0]
                        observation_nc4 = observation[0]
                        prediction_nc4 = prediction[0]

                        logging.info("this entry is from a missing html message")
                        logging.info("the netcdf4 datafile provided station {} timestamp {} observation {} prediction {}:"
                                     .format(crrt_station, datetimes_nc4, observation_nc4, prediction_nc4))

                        assert observation_nc4 > 1e8, ("observation: {}".format(observation_nc4))
                        assert prediction_nc4 > 1e8, ("predictino: {}".format(prediction_nc4))

                    else:
                        logging.warning("skipping test with datetime {} outside range".format(datetime_start_data))

            else:
                logging.warning("ignore {}: should be an iso string".format(iso_to_parse))