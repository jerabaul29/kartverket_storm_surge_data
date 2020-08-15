import numpy as np

from kartverket_stormsurge.helper.raise_assert import ras


def assert_strict_monotonic(array, list_dimensions=None):
    """Check that an array is strictly monotonic. Raise a
    ValueError if not.
    Input:
        - array: a numpy array of any dimension.
        - list_dimensions: the list of dimensions on which to do
            the check. Check all dimensions if None (default).
    Output: None.
    Can raise:
        a ValueError indicating the first non monotonic dimension.
    """

    if list_dimensions is None:
        n_dim = len(np.shape(array))
        list_dimensions = range(n_dim)
    else:
        ras(isinstance(list_dimensions, list))

    for dim in list_dimensions:
        dim_diff = np.diff(array, axis=dim)
        if not (np.all(dim_diff < 0) or np.all(dim_diff > 0)):
            raise ValueError("Array non stricly monotonic on dim {}".format(dim))


def find_index_first_greater_or_equal(np_array, value, tol=1e-6):
    """Find the index of the first value of np_array that is
    greater or equal than value.
    Input:
        - np_array: numpy array in which to look, should
            be monotonic and 1D.
        - value: the value to use as a reference for
            comparison.
        - tol: a tolerance for performing the comparison.
    Output:
        - the index of the first entry that is greater
            or equal to value.
    If no valid value, raise an error.
    """

    ras(isinstance(np_array, np.ndarray))
    np_array = np_array.squeeze()
    ras(len(np_array.shape) == 1)

    assert_strict_monotonic(np_array)

    if np_array[-1] < value:
        raise ValueError("no entry greater or equal than the asked value")

    first_index = np.argmax(np_array >= value - tol)

    return first_index
