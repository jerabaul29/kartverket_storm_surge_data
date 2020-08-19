"""Tests."""

import numpy as np

from kartverket_stormsurge.helper.arrays import find_index_first_greater_or_equal

def test_find_index_first_greater_or_equal_1():
    array_to_check = np.array([1.0, 2.0, 3.0])

    assert find_index_first_greater_or_equal(array_to_check, -5.0) == 0
    assert find_index_first_greater_or_equal(array_to_check, 1.0) == 0
    assert find_index_first_greater_or_equal(array_to_check, 1.2) == 1
    assert find_index_first_greater_or_equal(array_to_check, 2.0) == 1
