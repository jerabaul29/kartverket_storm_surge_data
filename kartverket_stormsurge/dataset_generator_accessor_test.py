"""A few tests against some requests done by hand:

# the answer is obtained from doing the request by hand:
# https://api.sehavniva.no/tideapi.php?stationcode=OSL&fromtime=2008-12-15T09:00:00+00&totime=2008-12-15T10:00:00+00&datatype=obs&refcode=&place=&file=&lang=&interval=10&dst=&tzone=utc&tide_request=stationdata
# <tide>
# <stationdata>
# <location name="OSLO" code="OSL" latitude="59.908559" longitude="10.734510">
# <data type="observation" unit="cm" reflevelcode="CD">
# <waterlevel value="27.3" time="2008-12-15T09:00:00+00:00" flag="obs"/>
# <waterlevel value="26.4" time="2008-12-15T09:10:00+00:00" flag="obs"/>
# <waterlevel value="25.6" time="2008-12-15T09:20:00+00:00" flag="obs"/>
# <waterlevel value="25.0" time="2008-12-15T09:30:00+00:00" flag="obs"/>
# <waterlevel value="24.6" time="2008-12-15T09:40:00+00:00" flag="obs"/>
# <waterlevel value="24.2" time="2008-12-15T09:50:00+00:00" flag="obs"/>
# <waterlevel value="23.8" time="2008-12-15T10:00:00+00:00" flag="obs"/>
# </data>
# <data type="prediction" unit="cm" reflevelcode="CD">
# <waterlevel value="56.1" time="2008-12-15T09:00:00+00:00" flag="pre"/>
# <waterlevel value="54.8" time="2008-12-15T09:10:00+00:00" flag="pre"/>
# <waterlevel value="53.6" time="2008-12-15T09:20:00+00:00" flag="pre"/>
# <waterlevel value="52.7" time="2008-12-15T09:30:00+00:00" flag="pre"/>
# <waterlevel value="51.9" time="2008-12-15T09:40:00+00:00" flag="pre"/>
# <waterlevel value="51.2" time="2008-12-15T09:50:00+00:00" flag="pre"/>
# <waterlevel value="50.6" time="2008-12-15T10:00:00+00:00" flag="pre"/>
# </data>
# </location>
# </stationdata>
# </tide>
"""

import os
import tempfile
import datetime
import numpy as np
import pytz

from kartverket_stormsurge.dataset_generator import DatasetGenerator
from kartverket_stormsurge.dataset_accessor import DatasetAccessor


def test_full_workflow_1():
    datetime_start_data = datetime.datetime(2008, 12, 15, 9, 0, 0, 0, pytz.utc)
    datetime_end_data = datetime.datetime(2008, 12, 28, 9, 0, 0, 0, pytz.utc)
    nc4_path = "./full_workflow_test.nc4"

    with tempfile.TemporaryDirectory() as tmpdirname:
        dataset_generator = DatasetGenerator(cache_folder=tmpdirname)
        dataset_generator.generate_netCDF4_dataset(datetime_start_data, datetime_end_data, nc4_path=nc4_path)

        dataset_accessor = DatasetAccessor(path_to_NetCDF=nc4_path)

        datetime_start_data_test = datetime.datetime(2008, 12, 15, 9, 0, 0, 0, pytz.utv)
        datetime_end_data_test = datetime.datetime(2008, 12, 15, 10, 0, 0, 0, pytz.utv)
        station_id = "OSL"

        data_timestamp, data_observation, data_prediction =\
            dataset_accessor.get_data(station_id,
                                      datetime_start_data_test,
                                      datetime_end_data_test)

        correct_datetime_timestamps = [datetime.datetime(2008, 12, 15, 9, 0),
                                       datetime.datetime(2008, 12, 15, 9, 10),
                                       datetime.datetime(2008, 12, 15, 9, 20),
                                       datetime.datetime(2008, 12, 15, 9, 30),
                                       datetime.datetime(2008, 12, 15, 9, 40),
                                       datetime.datetime(2008, 12, 15, 9, 50),
                                       datetime.datetime(2008, 12, 15, 10, 0)]

        correct_observation = [27.3, 26.4, 25.6, 25. , 24.6, 24.2, 23.8]
        correct_prediction = [56.1, 54.8, 53.6, 52.7, 51.9, 51.2, 50.6]

        assert correct_datetime_timestamps == datetime_timestamps
        assert np.allclose(np.array(correct_observation), observation)
        assert np.allclose(np.array(correct_prediction), prediction)       
        

    if os.path.exists(nc4_path):
        os.remove(nc4_path)
